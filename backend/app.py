from flask import Flask, render_template, request, jsonify, send_file, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import shutil
import io
import pandas as pd
import traceback
from fpdf import FPDF  # type: ignore
from services.db_init import init_db
from models import db, LedgerUpload
from services.ledger_parser import parse_sppu_ledger, generate_excel_from_data
from services.db_services import save_ledger_data_to_db
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt, JWTManager
from routes.auth_routes import auth_bp
# Load environment variables
load_dotenv()

# Adjust paths for backend/app.py location
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
UPLOADS_DIR = os.path.join(BASE_DIR, '..', 'uploads')
GENERATED_DIR = os.path.join(BASE_DIR, '..', 'generated')

app = Flask(__name__, 
            static_folder=os.path.join(FRONTEND_DIR, 'static'), 
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_url_path='/assets')
CORS(app)

# Database Configuration
# Use NeonDB for production, SQLite for local development
db_url = os.getenv('DATABASE_URL', 'sqlite:///local.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
# Fix for Windows/Neon: channel_binding can cause OperationalError
db_url = db_url.replace("&channel_binding=require", "").replace("channel_binding=require", "")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
app.config['GENERATED_FOLDER'] = GENERATED_DIR

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
from datetime import timedelta
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'new-secret-key-2026-v2')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')

db.init_app(app)

# Auto-initialize database tables and default admin when starting
with app.app_context():
    db.create_all()
    try:
        init_db()
    except Exception as e:
        print(f"Error during DB initialization: {e}")

# --- Global Data Storage (In-memory/File-based for Demo) ---
LATEST_DATA_PATH = os.path.join(app.config['GENERATED_FOLDER'], 'latest_report.xlsx')

@app.after_request
def add_header(response):
    """Ensure all API responses are never cached by the browser."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.errorhandler(422)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"msg": messages}), 422, headers
    else:
        return jsonify({"msg": messages}), 422

# Global cache to prevent severe hanging caused by reading Excel multiple times
_data_cache = {}

def get_data_path():
    from flask import request
    from flask_jwt_extended import get_jwt_identity
    from models import LedgerUpload
    
    upload_id = request.args.get('upload_id')
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str) if user_id_str else None
    
    data_path = None
    
    # If specific history is requested
    if upload_id:
        custom_path = os.path.join(app.config['GENERATED_FOLDER'], f'report_{upload_id}.xlsx')
        if os.path.exists(custom_path):
            data_path = custom_path
    
    # If no specific upload requested, default to the LATEST upload by THIS USER
    if not data_path and user_id:
        latest_upload = LedgerUpload.query.filter_by(uploaded_by=user_id).order_by(LedgerUpload.upload_date.desc()).first()
        if latest_upload:
            custom_path = os.path.join(app.config['GENERATED_FOLDER'], f'report_{latest_upload.id}.xlsx')
            if os.path.exists(custom_path):
                data_path = custom_path
                
    # ENFORCE STRICT ISOLATION: 
    # If the user hasn't uploaded any data, we intentionally return None
    # so the dashboard reads empty rather than stealing LATEST_DATA_PATH
    if not data_path:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims and claims.get('role') == 'admin':
            data_path = LATEST_DATA_PATH
        else:
            return None
        
    return data_path

def get_data():
    """Helper to load the latest or specific processed data with caching to prevent hangs."""
    data_path = get_data_path()

    if data_path and os.path.exists(data_path):
        try:
            mtime = os.path.getmtime(data_path)
            # Return cached dataframe if file hasn't changed
            if data_path in _data_cache and _data_cache[data_path]['mtime'] == mtime:
                return _data_cache[data_path]['df'].copy()

            # Load 'All Students' sheet which contains the combined data
            df = pd.read_excel(data_path, sheet_name='All Students')
            if 'branch' in df.columns:
                # Clean up existing data's branch column
                df['branch'] = df['branch'].astype(str).str.split('(?i)Date of Printing').str[0].str.strip()
            
            # Update cache
            _data_cache[data_path] = {'mtime': mtime, 'df': df}
            return df.copy()
        except Exception as e:
            print(f"Error reading data: {e}")
            return pd.DataFrame() # Empty
    return pd.DataFrame()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static_pages(filename):
    # Check if file exists in templates
    template_path = os.path.join(app.template_folder, filename)
    if os.path.exists(template_path):
        return render_template(filename)
    return f"File not found: {filename}", 404

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    
    # Handle non-HTTP exceptions
    traceback.print_exc()
    return jsonify({"error": "An unexpected internal server error occurred.", "details": str(e)}), 500

# --- API Endpoints ---

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_ledger():
    if 'ledger' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['ledger']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        try:
            file.save(filepath)
            
            # 1. Parse PDF
            students = parse_sppu_ledger(filepath)
            
            # 2. Generate and Save Excel (Sources of Truth)
            df = generate_excel_from_data(students, LATEST_DATA_PATH)
            
            # FORCE CACHE INVALIDATION: clear any memory holds on the previous dashboard data
            _data_cache.clear()
            
            # 3. Save to Ledger History (DB)
            if not df.empty:
                total = len(df)
                passed = len(df[df['status'] == 'Pass'])
                failed = len(df[df['status'] == 'Fail'])
                
                # Get current user identity
                # identity is now a string (user_id)
                current_user_id_str = get_jwt_identity()
                user_id = int(current_user_id_str) if current_user_id_str else None

                # Create Record
                upload_record = LedgerUpload(
                    filename=file.filename,
                    uploaded_by=user_id,
                    academic_year="2023-2024", # Simplification: extract from filename or PDF later
                    semester="2",              # Simplification
                    total_students=total,
                    pass_count=passed,
                    fail_count=failed
                )
                db.session.add(upload_record)
                db.session.commit()
                
                # Copy excel to history
                history_excel_path = os.path.join(app.config['GENERATED_FOLDER'], f'report_{upload_record.id}.xlsx')
                shutil.copy(LATEST_DATA_PATH, history_excel_path)
                
                # Save parsed data to Relational DB Tables
                try:
                    save_ledger_data_to_db(students, upload_record.id, "2023-2024", "2")
                except Exception as db_err:
                    print(f"Error saving relational DB data: {db_err}")
                    traceback.print_exc()
                    # We continue even if this fails to not break the existing flow abruptly,
                    # but the error will be in the logs.

            return jsonify({
                "message": "File processed successfully",
                "students_processed": len(df),
                "success": True,
                "upload_id": upload_record.id if not df.empty else None
            })
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            traceback.print_exc() # Critical for debugging
            return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_upload_history():
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str else None
        
        # Only fetch uploads for the CURRENT user
        uploads = LedgerUpload.query.filter_by(uploaded_by=user_id).order_by(LedgerUpload.upload_date.desc()).all()
        results = []
        seen_filenames = set()
        
        for u in uploads:
            if u.filename in seen_filenames:
                continue
            seen_filenames.add(u.filename)
            
            perc = round((u.pass_count / u.total_students) * 100, 1) if u.total_students > 0 else 0
            results.append({
                "id": u.id,
                "filename": u.filename,
                "upload_date": u.upload_date.strftime('%Y-%m-%d %H:%M'),
                "academic_year": u.academic_year,
                "semester": u.semester,
                "total_students": u.total_students,
                "pass_percentage": perc,
                "pass_count": u.pass_count,
                "fail_count": u.fail_count
            })
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify([])

@app.route('/api/history/<int:upload_id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(upload_id):
    try:
        upload = LedgerUpload.query.get(upload_id)
        if not upload:
            return jsonify({"error": "Upload not found"}), 404
            
        # Delete from DB
        db.session.delete(upload)
        db.session.commit()
        
        # Also clean up generated files if desired (optional)
        filename = f"report_{upload_id}.xlsx"
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return jsonify({"message": "Successfully deleted"}), 200
    except Exception as e:
        print(f"Error deleting history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    df = get_data()
    if df.empty:
        # Return zeros if no data yet
        return jsonify({
            "totalStudents": 0, "passPercentage": 0,
            "passedStudents": 0,
            "failedStudents": 0, "atktCount": 0,
            "collegeTopper": None
        })
    
    total = int(len(df))
    passed = int(len(df[df['status'] == 'Pass']))
    failed = int(len(df[df['status'] == 'Fail']))
    pass_percentage = float(round((passed / total) * 100, 2)) if total > 0 else 0.0
    
    # Identify Topper
    if 'sgpa' in df.columns:
        # Convert to numeric just in case
        df['sgpa_numeric'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0)
        topper_row = df.loc[df['sgpa_numeric'].idxmax()]
        topper = {
            "name": str(topper_row.get('name', '')),
            "branch": str(topper_row.get('branch', 'Unknown')),
            "percentage": float(topper_row['sgpa_numeric'])
        }
    else:
        topper = None

    return jsonify({
        "totalStudents": total,
        "passedStudents": passed,
        "passPercentage": pass_percentage,
        "failedStudents": failed,
        "atktCount": 0, # Placeholder
        "collegeTopper": topper
    })

@app.route('/api/analysis/branch', methods=['GET'])
@jwt_required()
def get_branch_analysis():
    df = get_data()
    if df.empty: return jsonify([])
    
    results = []
    # Group by Branch
    if 'branch' in df.columns:
        grouped = df.groupby('branch')
        for name, group in grouped:
            total = len(group)
            passed = len(group[group['status'] == 'Pass'])
            pass_perc = round((passed / total) * 100, 1) if total > 0 else 0
            
            # Calculate Avg Marks (SGPA)
            avg_sgpa = round(group['sgpa'].mean(), 2) if 'sgpa' in group.columns else 0
            
            # Branch Topper
            topper_name = ""
            if 'sgpa' in group.columns and not group.empty:
                t_row = group.loc[group['sgpa'].idxmax()]
                topper_name = t_row['name']

            results.append({
                "name": name,
                "passPercentage": pass_perc,
                "avgMarks": avg_sgpa * 10, # Convert SGPA to approx marks for view
                "topper": topper_name
            })
            
    return jsonify(results)

@app.route('/api/analysis/failed', methods=['GET'])
@jwt_required()
def get_failed_students():
    df = get_data()
    if df.empty: return jsonify([])
    
    failed_df = df[df['status'] == 'Fail']
    # Convert to list of dicts
    return jsonify(failed_df.to_dict(orient='records'))

@app.route('/api/analysis/merit', methods=['GET'])
@jwt_required()
def get_merit_list():
    df = get_data()
    if df.empty: return jsonify([])
    
    # Get user role for filtering (Security - Optional/Future Use)
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_branch_id = claims.get('branch_id')
    except Exception:
        user_role = None
        user_branch_id = None
    
    # Filter by Branch/Year
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]

    # Sort by SGPA desc
    if 'sgpa' in df.columns:
        merit_df = df.sort_values(by='sgpa', ascending=False).head(10)
        # Add Rank
        merit_df['rank'] = range(1, len(merit_df) + 1)
        
        # Select required columns for frontend to avoid NaN parsing issues
        columns_to_return = ['rank', 'name', 'branch', 'sgpa', 'prn', 'seat_no']
        available_columns = [col for col in columns_to_return if col in merit_df.columns]
        
        merit_df = merit_df[available_columns].fillna('')
        return jsonify(merit_df.to_dict(orient='records'))
    return jsonify([])

@app.route('/api/analysis/grades', methods=['GET'])
@jwt_required()
def get_grade_dist():
    df = get_data()
    if df.empty: return jsonify([])
    
    # Calculate Grade directly based on SPPU SGPA bounds
    if 'sgpa' not in df.columns: return jsonify([])
    
    # Bins: [0, 4.0), [4.0, 5.0), [5.0, 5.5), [5.5, 6.0), [6.0, 7.0), [7.0, 8.0), [8.0, 9.0), [9.0, 10.1)
    bins = [0, 4.0, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.1]
    labels = ['F', 'P', 'C', 'B', 'B+', 'A', 'A+', 'O']
    
    # Convert any string SGPAs to numeric just in case
    df['sgpa_numeric'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0)
    df['calculated_grade'] = pd.cut(df['sgpa_numeric'], bins=bins, labels=labels, right=False)
    
    # Filter by Branch/Year
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]

    dist = df['calculated_grade'].value_counts().reindex(labels, fill_value=0)
    return jsonify(dist.to_dict())

@app.route('/api/analysis/performance-bands', methods=['GET'])
@jwt_required()
def get_performance_bands():
    df = get_data()
    if df.empty: return jsonify({"Above 80%": 0, "60-80%": 0, "40-60%": 0, "Below 40%": 0})
    
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]
        
    df['percentage'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0) * 8.9
    
    bands = {
        "Above 80%": len(df[df['percentage'] >= 80]),
        "60-80%": len(df[(df['percentage'] >= 60) & (df['percentage'] < 80)]),
        "40-60%": len(df[(df['percentage'] >= 40) & (df['percentage'] < 60)]),
        "Below 40%": len(df[df['percentage'] < 40])
    }
    return jsonify(bands)

@app.route('/api/analysis/marks-distribution', methods=['GET'])
@jwt_required()
def get_marks_distribution():
    df = get_data()
    if df.empty: return jsonify({"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0})
    
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]
        
    df['percentage'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0) * 8.9
    
    ranges = {
        "0-20": len(df[df['percentage'] <= 20]),
        "21-40": len(df[(df['percentage'] > 20) & (df['percentage'] <= 40)]),
        "41-60": len(df[(df['percentage'] > 40) & (df['percentage'] <= 60)]),
        "61-80": len(df[(df['percentage'] > 60) & (df['percentage'] <= 80)]),
        "81-100": len(df[df['percentage'] > 80])
    }
    return jsonify(ranges)

@app.route('/api/analysis/failed-pattern', methods=['GET'])
@jwt_required()
def get_failed_pattern():
    df = get_data()
    if df.empty: return jsonify({"1 subject": 0, "2-3 subjects": 0, "4+ subjects": 0})
    
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]
        
    data_path = get_data_path()
    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        failed_subs = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail']
        fail_counts = failed_subs.groupby('seat_no').size().reset_index(name='failed_count')
    except Exception:
        fail_counts = pd.DataFrame(columns=['seat_no', 'failed_count'])

    df = df.merge(fail_counts, on='seat_no', how='left')
    df['failed_count'] = df['failed_count'].fillna(0)
    
    patterns = {
        "1 subject": len(df[df['failed_count'] == 1]),
        "2-3 subjects": len(df[(df['failed_count'] >= 2) & (df['failed_count'] <= 3)]),
        "4+ subjects": len(df[df['failed_count'] >= 4])
    }
    return jsonify(patterns)

@app.route('/api/analytics/trend', methods=['GET'])
@jwt_required()
def get_trend_analysis():
    # Fetch from DB LedgerUploads
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str else None
        
        uploads = LedgerUpload.query.filter_by(uploaded_by=user_id).order_by(LedgerUpload.upload_date).all()
        if not uploads:
            # Mock data if empty for demo
            return jsonify([
                {"year": "2021-2022", "passPercentage": 78},
                {"year": "2022-2023", "passPercentage": 82},
                {"year": "2023-2024", "passPercentage": 65}
            ])
        
        data = []
        for u in uploads:
            perc = round((u.pass_count / u.total_students) * 100, 1) if u.total_students > 0 else 0
            data.append({
                "year": u.academic_year + " (" + u.upload_date.strftime('%b') + ")",
                "passPercentage": perc
            })
        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify([])

@app.route('/api/analytics/at-risk', methods=['GET'])
@jwt_required()
def get_at_risk_students():
    df = get_data()
    if df.empty: return jsonify([])
    
    branch = request.args.get('branch')
    if branch and branch != 'all':
        df = df[df['branch'] == branch]
    
    df['percentage'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0) * 8.9
    
    data_path = get_data_path()
    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        failed_subs = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail']
        fail_counts = failed_subs.groupby('seat_no').size().reset_index(name='failed_count')
    except Exception:
        fail_counts = pd.DataFrame(columns=['seat_no', 'failed_count'])

    df = df.merge(fail_counts, on='seat_no', how='left')
    df['failed_count'] = df['failed_count'].fillna(0)
    
    # Criteria: Percentage < 40 OR Failed >= 2 (At Risk). Failed > 3 (Critical)
    df['is_at_risk'] = (df['percentage'] < 40) | (df['failed_count'] >= 2)
    df['is_critical'] = df['failed_count'] > 3
    
    # Filter
    filtered = df[df['is_at_risk'] | df['is_critical']].copy()
    if filtered.empty: return jsonify([])
    
    filtered['risk_status'] = filtered.apply(lambda row: 'Critical' if row['is_critical'] else 'At Risk', axis=1)
    
    # To show percentage nicely
    filtered['percentage'] = filtered['percentage'].round(2)
    
    filtered = filtered.fillna('')
    cols = ['seat_no', 'prn', 'name', 'percentage', 'failed_count', 'risk_status']
    if 'branch' in filtered.columns:
        cols.append('branch')
        
    return jsonify(filtered[cols].to_dict(orient='records'))

@app.route('/api/student/<seat_no>', methods=['GET'])
@jwt_required()
def get_student_record(seat_no):
    df = get_data()
    if df.empty: return jsonify({"error": "No data available"}), 404
    
    student_df = df[df['seat_no'] == seat_no]
    if student_df.empty: return jsonify({"error": "Student not found"}), 404
    
    student_data = student_df.iloc[0].fillna('').to_dict()
    return jsonify(student_data)

@app.route('/api/analysis/subjects', methods=['GET'])
@jwt_required()
def get_subject_analysis():
    data_path = get_data_path()
    if os.path.exists(data_path):
        try:
            sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
            if sub_df.empty: return jsonify([])
            
            # Clean up messy university subject prefixes
            if 'subject_name' in sub_df.columns:
                sub_df['subject_name'] = sub_df['subject_name'].astype(str).apply(lambda x: x.split('*')[-1].strip() if '*' in x else x)
            
            # Extract outof to group them separately if they have the same name but different max marks
            if 'marks' in sub_df.columns and 'subject_name' in sub_df.columns:
                sub_df['outof_max'] = pd.to_numeric(sub_df['marks'].astype(str).str.split('/').str.get(1), errors='coerce').fillna(0).astype(int)
                
                # Format Subject based on marks logic
                def format_subj(row):
                    n = str(row['subject_name'])
                    o = row['outof_max']
                    if o == 50 and not n.endswith('Lab'):
                        n = f"{n} Lab"
                    elif o == 25:
                        if n.endswith(' Lab'): n = n[:-4]
                        if n.endswith(' Tutorial'): n = n[:-9]
                        if not n.endswith(' TW'): n = f"{n} TW"
                    return n.strip()
                
                sub_df['subject_name'] = sub_df.apply(format_subj, axis=1)
            else:
                sub_df['outof_max'] = 0
            
            try:
                all_students_df = pd.read_excel(data_path, sheet_name='All Students')
                if 'name' in all_students_df.columns and 'seat_no' in all_students_df.columns:
                    # also extract 'branch' and 'prn'
                    cols_to_extract = ['seat_no', 'name', 'branch'] if 'branch' in all_students_df.columns else ['seat_no', 'name']
                    if 'prn' in all_students_df.columns:
                        cols_to_extract.append('prn')
                    name_mapping = all_students_df[cols_to_extract].drop_duplicates()
                    sub_df = sub_df.merge(name_mapping, on='seat_no', how='left')
            except Exception:
                pass

            branch = request.args.get('branch')
            if branch and branch != 'all' and 'branch' in sub_df.columns:
                sub_df = sub_df[sub_df['branch'] == branch]

            results = []
            grouped = sub_df.groupby(['subject_name', 'outof_max'])
            
            for (name, outof_val), group in grouped:
                total = len(group)
                if total == 0: continue
                
                passed_count = len(group[group['status'] == 'Pass'])
                failed_count = len(group[group['status'] == 'Fail'])
                pass_perc = round((passed_count / total) * 100, 1)
                
                topper_name = "-"
                
                # Calculate Highest/Lowest Marks and Average Marks
                avg_marks = 0
                if 'marks' in group.columns:
                    marks_split = group['marks'].astype(str).str.split('/')
                    numeric_marks = pd.to_numeric(marks_split.str[0], errors='coerce')
                    highest = numeric_marks.max()
                    lowest = numeric_marks.min()
                    avg_val = numeric_marks.mean()
                    highest_marks = int(highest) if pd.notna(highest) else "-"
                    lowest_marks = int(lowest) if pd.notna(lowest) else "-"
                    avg_marks = float(round(avg_val, 1)) if pd.notna(avg_val) else 0.0
                    
                    if not group.empty and pd.notna(highest) and 'name' in group.columns:
                        top_rows = group[numeric_marks == highest]
                        if not top_rows.empty:
                            t_list = []
                            for _, r in top_rows.iterrows():
                                n = r.get('name', '')
                                n_str = str(n) if pd.notna(n) else "-"
                                t_list.append(n_str)
                            seen = set()
                            unique_toppers = [t for t in t_list if not (t in seen or seen.add(t))]
                            topper_name = "<br>".join(unique_toppers)
                else:
                    highest_marks = "-"
                    lowest_marks = "-"
                    outof_val = 0
                
                results.append({
                    "name": name,
                    "pass": pass_perc,
                    "fail": failed_count,
                    "total": total,
                    "highest": highest_marks,
                    "lowest": lowest_marks,
                    "avgMarks": avg_marks,
                    "outof": outof_val,
                    "topper": topper_name
                })
                
            # Sort by Fail Rate desc (Finding difficult subjects)
            # return sorted(results, key=lambda x: x['pass'])
            return jsonify(results)
        except Exception as e:
            print(f"Error loading subject data: {e}")
            return jsonify([])
            
    return jsonify([])

@app.route('/api/analysis/subjects/students', methods=['GET'])
@jwt_required()
def get_subject_students():
    subject_param = request.args.get('subject')
    outof_param = request.args.get('outof')
    if not subject_param:
        return jsonify({"error": "Subject parameter is required"}), 400

    data_path = get_data_path()
    if not os.path.exists(data_path):
        return jsonify([])

    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        all_df = pd.read_excel(data_path, sheet_name='All Students')

        # Clean up messy university subject prefixes to match UI parameters
        if 'subject_name' in sub_df.columns:
            sub_df['subject_name'] = sub_df['subject_name'].astype(str).apply(lambda x: x.split('*')[-1].strip() if '*' in x else x)

        if 'marks' in sub_df.columns and 'subject_name' in sub_df.columns:
            sub_df['outof_max'] = pd.to_numeric(sub_df['marks'].astype(str).str.split('/').str.get(1), errors='coerce').fillna(0).astype(int)
            def format_subj(row):
                n = str(row['subject_name'])
                o = row['outof_max']
                if o == 50 and not n.endswith('Lab'):
                    n = f"{n} Lab"
                elif o == 25:
                    if n.endswith(' Lab'): n = n[:-4]
                    if n.endswith(' Tutorial'): n = n[:-9]
                    if not n.endswith(' TW'): n = f"{n} TW"
                return n.strip()
            sub_df['subject_name'] = sub_df.apply(format_subj, axis=1)

        # Filter
        filtered = sub_df[sub_df['subject_name'] == subject_param].copy()
        
        if outof_param and 'marks' in filtered.columns:
            filtered['outof_max'] = pd.to_numeric(filtered['marks'].astype(str).str.split('/').str.get(1), errors='coerce').fillna(0).astype(int)
            filtered = filtered[filtered['outof_max'] == int(outof_param)]
            
        if filtered.empty: return jsonify([])

        # Join for name, branch, prn
        if 'name' in all_df.columns and 'seat_no' in all_df.columns:
            cols_to_extract = ['seat_no', 'name', 'branch'] if 'branch' in all_df.columns else ['seat_no', 'name']
            if 'prn' in all_df.columns:
                cols_to_extract.append('prn')
            name_mapping = all_df[cols_to_extract].drop_duplicates()
            filtered = filtered.merge(name_mapping, on='seat_no', how='left')

        # Sort logically by numeric marks
        if 'marks' in filtered.columns:
            filtered['numeric_marks'] = pd.to_numeric(filtered['marks'].astype(str).str.split('/').str[0], errors='coerce')
        else:
            filtered['numeric_marks'] = 0

        if 'status' in filtered.columns:
            filtered['is_pass'] = filtered['status'].astype(str).str.strip().str.title().apply(lambda x: 1 if x == 'Pass' else 0)
            filtered = filtered.sort_values(by=['is_pass', 'numeric_marks'], ascending=[False, False]).fillna('')
        else:
            filtered = filtered.sort_values(by='numeric_marks', ascending=False).fillna('')
        
        cols = ['seat_no', 'prn', 'name', 'branch', 'marks', 'tw_pr', 'status']
        available_cols = [c for c in cols if c in filtered.columns]
        
        return jsonify(filtered[available_cols].to_dict(orient='records'))

    except Exception as e:
        print(f"Error fetching subject students: {e}")
        return jsonify([])

@app.route('/api/report/download', methods=['GET'])
@jwt_required()
def download_report():
    upload_id = request.args.get('upload_id')
    data_path = LATEST_DATA_PATH
    download_name = 'Generated_Result_Report.xlsx'

    if upload_id:
        custom_path = os.path.join(app.config['GENERATED_FOLDER'], f'report_{upload_id}.xlsx')
        if os.path.exists(custom_path):
            data_path = custom_path
            record = LedgerUpload.query.get(upload_id)
            if record and record.filename:
                base = os.path.splitext(record.filename)[0]
                download_name = f"{base}.xlsx"
    else:
        record = LedgerUpload.query.order_by(LedgerUpload.upload_date.desc()).first()
        if record and record.filename:
            base = os.path.splitext(record.filename)[0]
            download_name = f"{base}.xlsx"

    if os.path.exists(data_path):
        return send_file(
            data_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=download_name
        )
    return jsonify({"error": "Report not found"}), 404
def generate_pdf_table(title, df, columns):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    col_widths = {
        'prn': 25, 'seat_no': 25, 'name': 55, 'branch': 25, 'sgpa': 15, 'status': 15, 'subject_name': 60, 'marks': 25,
        'failed_subjects': 70
    }
    
    pdf.set_font("Helvetica", style='B', size=9)
    for col in columns:
        w = col_widths.get(col, 30)
        pdf.cell(w, 8, str(col).replace('_', ' ').title(), border=1)
    pdf.cell(0, 8, "", new_x="LMARGIN", new_y="NEXT") # New line
    
    pdf.set_font("Helvetica", size=8)
    for _, row in df.iterrows():
        for col in columns:
            w = col_widths.get(col, 30)
            val = str(row.get(col, ''))
            # Truncate to fit roughly
            if len(val) > int(w/1.5): val = val[:int(w/1.5)] + '..'
            pdf.cell(w, 8, val, border=1)
        pdf.cell(0, 8, "", new_x="LMARGIN", new_y="NEXT")
        
    pdf_bytes = pdf.output()
    return io.BytesIO(pdf_bytes)

def handle_multi_format_download(df, filename_prefix, pdf_cols):
    req_format = request.args.get('format', 'xlsx').lower()
    
    if req_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    elif req_format == 'pdf':
        try:
            output = generate_pdf_table(filename_prefix.replace('_', ' '), df, pdf_cols)
            return send_file(
                output, mimetype='application/pdf',
                as_attachment=True, download_name=f'{filename_prefix}.pdf'
            )
        except Exception as e:
            print(f"PDF creation error: {e}")
            req_format = 'csv' # force fallback to csv
            output = io.StringIO()
            df.to_csv(output, index=False)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}.csv'
            response.headers['Content-type'] = 'text/csv'
            return response
    else:
        # Default XLSX
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        return send_file(
            output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, download_name=f'{filename_prefix}.xlsx'
        )

@app.route('/api/reports/remedial', methods=['GET'])
@jwt_required()
def report_remedial():
    data_path = get_data_path()
    if not os.path.exists(data_path): return jsonify({"error": "No data"}), 404
    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        all_df = pd.read_excel(data_path, sheet_name='All Students')
        
        if 'name' in all_df.columns:
            sub_df = sub_df.merge(all_df[['seat_no', 'name', 'prn']], on='seat_no', how='left')
        
        remedial = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail'].copy()
        remedial['email'] = 'adityamagdum0928@gmail.com'
        
        pdf_cols = ['name', 'seat_no', 'subject_name', 'marks', 'status', 'email']
        available = [c for c in pdf_cols if c in remedial.columns]
        return handle_multi_format_download(remedial, 'Remedial_Students_Report', available)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/subject-weak', methods=['GET'])
@jwt_required()
def report_subject_weak():
    data_path = get_data_path()
    if not os.path.exists(data_path): return jsonify({"error": "No data"}), 404
    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        all_df = pd.read_excel(data_path, sheet_name='All Students')
        if 'name' in all_df.columns:
            sub_df = sub_df.merge(all_df[['seat_no', 'name']], on='seat_no', how='left')
            
        weak = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail'].copy()
        weak['numeric_marks'] = pd.to_numeric(weak['marks'].astype(str).str.split('/').str[0], errors='coerce')
        
        grouped = weak.groupby('subject_name').agg(
            student_list=('name', lambda x: ', '.join(x.dropna().astype(str))),
            average_marks=('numeric_marks', 'mean')
        ).reset_index()
        
        grouped['average_marks'] = grouped['average_marks'].round(1)
        
        pdf_cols = ['subject_name', 'average_marks', 'student_list']
        return handle_multi_format_download(grouped, 'Subject_Weak_Students', pdf_cols)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/class-summary', methods=['GET'])
@jwt_required()
def report_class_summary():
    df = get_data()
    if df.empty: return jsonify({"error": "No data available."}), 404
    
    total = len(df)
    passed = len(df[df['status'] == 'Pass'])
    failed = len(df[df['status'] == 'Fail'])
    
    pass_perc = round((passed / total) * 100, 1) if total > 0 else 0
    fail_perc = round((failed / total) * 100, 1) if total > 0 else 0
    
    if 'total_marks' in df.columns:
        numeric = pd.to_numeric(df['total_marks'], errors='coerce').dropna()
        avg_marks = round(numeric.mean(), 1) if not numeric.empty else 0
        hi_marks = numeric.max() if not numeric.empty else 0
        lo_marks = numeric.min() if not numeric.empty else 0
    else:
        avg_marks = hi_marks = lo_marks = 0
        
    summary_df = pd.DataFrame([{
        'total_students': total,
        'pass_percentage': f"{pass_perc}%",
        'fail_percentage': f"{fail_perc}%",
        'average_marks': avg_marks,
        'highest_marks': hi_marks,
        'lowest_marks': lo_marks
    }])
    
    pdf_cols = summary_df.columns.tolist()
    return handle_multi_format_download(summary_df, 'Class_Performance_Summary', pdf_cols)

@app.route('/api/reports/progress', methods=['GET'])
@jwt_required()
def report_progress():
    df = get_data()
    if df.empty: return jsonify({"error": "No data available."}), 404
    
    insem_cols = [c for c in df.columns if c.endswith('_INSEM')]
    ese_cols = [c for c in df.columns if c.endswith('_ESE')]
    
    results = []
    for _, row in df.iterrows():
        total_insem = 0
        total_ese = 0
        insem_count = 0
        ese_count = 0
        
        for c in insem_cols:
            val = pd.to_numeric(row.get(c, 0), errors='coerce')
            if pd.notna(val):
                total_insem += val
                insem_count += 1
                
        for c in ese_cols:
            val = pd.to_numeric(row.get(c, 0), errors='coerce')
            if pd.notna(val):
                total_ese += val
                ese_count += 1
                
        insem_perc = (total_insem / (30 * insem_count)) * 100 if insem_count > 0 else 0
        ese_perc = (total_ese / (70 * ese_count)) * 100 if ese_count > 0 else 0
        
        improvement = ese_perc - insem_perc
        
        results.append({
            'name': row.get('name', 'Unknown'),
            'seat_no': row.get('seat_no', ''),
            'previous_performance_insem': f"{round(insem_perc, 1)}%",
            'current_performance_ese': f"{round(ese_perc, 1)}%",
            'improvement_delta': f"{round(improvement, 1)}%"
        })
        
    prog_df = pd.DataFrame(results)
    pdf_cols = ['name', 'seat_no', 'previous_performance_insem', 'current_performance_ese', 'improvement_delta']
    return handle_multi_format_download(prog_df, 'Student_Progress_Report', pdf_cols)

@app.route('/api/reports/action-recommendation', methods=['GET'])
@jwt_required()
def report_action_recommendation():
    df = get_data()
    if df.empty: return jsonify({"error": "No data available."}), 404
    
    data_path = get_data_path()
    try:
        sub_df = pd.read_excel(data_path, sheet_name='Subjectwise')
        fail_counts = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail'].groupby('seat_no').size().reset_index(name='failed_count')
    except:
        fail_counts = pd.DataFrame(columns=['seat_no', 'failed_count'])
        
    df = df.merge(fail_counts, on='seat_no', how='left')
    df['failed_count'] = df['failed_count'].fillna(0)
    df['percentage'] = pd.to_numeric(df['sgpa'], errors='coerce').fillna(0) * 8.9
    
    def get_recommendation(row):
        if row['failed_count'] >= 2:
            return "Needs Remedial Class (Priority Intervention)"
        elif row['percentage'] > 0 and row['percentage'] < 50:
            return "Requires Practice (Borderline)"
        else:
            return "Monitor Performance (On Track)"
            
    df['action_recommendation'] = df.apply(get_recommendation, axis=1)
    
    out_df = df[['seat_no', 'name', 'percentage', 'failed_count', 'action_recommendation']].copy()
    out_df['percentage'] = out_df['percentage'].round(1).astype(str) + '%'
    
    pdf_cols = ['seat_no', 'name', 'percentage', 'failed_count', 'action_recommendation']
    return handle_multi_format_download(out_df, 'Action_Recommendations', pdf_cols)

@app.route('/api/notify-remedial', methods=['POST'])
@jwt_required()
def notify_remedial_students():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    sender_email = os.getenv('EMAIL_SENDER', 'pictsppu@gmail.com')
    sender_password = os.getenv('EMAIL_PASSWORD')
    
    if not sender_password:
        return jsonify({"error": "Email password not configured in backend .env"}), 500
        
    data = request.get_json() or {}
    schedule_date = data.get('date', 'TBD')
    schedule_time = data.get('time', 'TBD')
    schedule_venue = data.get('venue', 'A-207 Classroom')
    schedule_topic = data.get('topic', 'Remedial Session')
        
    recipient_emails = ["adityamagdum0928@gmail.com", "girya03@gmail.com"]
    
    subject = f"📢 Extra Lecture Scheduled - {schedule_topic}"
    body_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; max-width: 600px; margin: auto; }}
            .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }}
            .details {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; border-radius: 4px; }}
            .details ul {{ list-style-type: none; padding-left: 0; }}
            .details li {{ margin-bottom: 8px; }}
            .footer {{ margin-top: 30px; font-size: 0.9em; color: #666; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="header">{schedule_topic} Notification</h2>
            <p>Dear Student,</p>
            <p>This is to inform you that an extra lecture has been scheduled for students in the remedial section.</p>
            
            <div class="details">
                <strong>Lecture Details:</strong>
                <ul>
                    <li>📅 <strong>Date:</strong> {schedule_date}</li>
                    <li>⏰ <strong>Time:</strong> {schedule_time}</li>
                    <li>📍 <strong>Venue:</strong> {schedule_venue}</li>
                </ul>
            </div>
            
            <p>You are requested to attend the class without fail to improve your academic performance.</p>
            
            <div class="footer">
                <p>Best Regards,<br>
                <strong>Subject Teacher</strong><br>
                <em>(Automated Notification System)</em></p>
            </div>
        </div>
    </body>
    </html>
    """

    
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = "PICT AUTONOMOUS <pictsppu@gmail.com>"
    msg['To'] = ", ".join(recipient_emails)
    
    msg.attach(MIMEText(body_html, "html"))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()
        return jsonify({"message": "Remedial session email sent successfully"}), 200
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

# --- Main ---
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            init_db()  # Seed Admin User
        except Exception as e:
            print(f"DB Init Error: {e}")
            pass

    print("Starting RESULT LEDGER Flask server...")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
