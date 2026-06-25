from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preprocessing'))
from ledger_parser import parse_sppu_ledger, generate_excel_from_data

app = Flask(__name__)
CORS(app)

# Setup directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
GENERATED_DIR = os.path.join(PROJECT_ROOT, 'generated')
UPLOADS_DIR = os.path.join(BACKEND_DIR, 'uploads')

os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.route('/parse', methods=['POST'])
def parse():
    if 'ledger' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['ledger']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    upload_id = request.form.get('upload_id')
    if not upload_id:
        return jsonify({"error": "Missing upload_id"}), 400

    temp_path = os.path.join(UPLOADS_DIR, file.filename)
    file.save(temp_path)
    
    try:
        students_list = parse_sppu_ledger(temp_path)
        
        # Generate the excel file
        excel_filename = f"report_{upload_id}.xlsx"
        excel_path = os.path.join(GENERATED_DIR, excel_filename)
        generate_excel_from_data(students_list, excel_path)
        
        return jsonify({"success": True, "upload_id": upload_id, "students": students_list})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    port = int(os.environ.get('PYTHON_PORT', 5002))
    print(f"[Python Microservice] Starting PDF Parser on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
