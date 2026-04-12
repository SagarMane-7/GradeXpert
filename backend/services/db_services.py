from models import db, Branch, Student, Subject, Marks
import re

def save_ledger_data_to_db(students_data, upload_id, academic_year, semester):
    """
    Upserts (Updates or Inserts) parsed ledger data into database.
    Optimized to eliminate N+1 latency using local caches.
    """
    branch_cache = {}
    subject_cache = {}

    for student_data in students_data:
        # 1. UPSERT Branch
        branch_name = student_data.get('branch', 'Unknown')
        if branch_name not in branch_cache:
            branch = Branch.query.filter_by(name=branch_name).first()
            if not branch:
                branch = Branch(name=branch_name)
                db.session.add(branch)
                db.session.commit()
            branch_cache[branch_name] = branch.id
            
        branch_id = branch_cache[branch_name]

        # 2. UPSERT Student
        seat_no = student_data.get('seat_no')
        student = Student.query.filter_by(seat_no=seat_no).first()
        if not student:
            student = Student(seat_no=seat_no)
            db.session.add(student)
            
        student.name = student_data.get('name', '')
        student.branch_id = branch_id
        student.academic_year = academic_year
        student.upload_id = upload_id
        db.session.commit() # Need ID for Marks

        # 3. UPSERT Subjects and Marks
        subjects_list = student_data.get('subjects_list', [])
        for sub_data in subjects_list:
            subject_name = sub_data.get('subject_name')
            try:
                sem_int = int(semester)
            except ValueError:
                sem_int = 1 # Fallback

            # Subject Cache Key
            subj_key = f"{subject_name}_{branch_id}_{sem_int}"
            
            if subj_key not in subject_cache:
                subject = Subject.query.filter_by(name=subject_name, branch_id=branch_id, semester=sem_int).first()
                if not subject:
                    subject = Subject(name=subject_name, branch_id=branch_id, semester=sem_int)
                    db.session.add(subject)
                    db.session.commit()
                subject_cache[subj_key] = subject.id
                
            subject_id = subject_cache[subj_key]

            # Parse Marks
            marks_str = str(sub_data.get('marks', '')).strip()
            found_grade = sub_data.get('grade', '')
            
            marks_obtained = 0.0
            max_marks = 100.0
            grade = found_grade

            if marks_str:
                match = re.search(r'(\d+)\s*/\s*(\d+)', marks_str)
                if match:
                    marks_obtained = float(match.group(1))
                    max_marks = float(match.group(2))
                else:
                    if marks_str.isdigit():
                        marks_obtained = float(marks_str)
                    else:
                        grade = 'F'
                        marks_obtained = 0.0

            if not grade or str(grade).upper() in ['AB', 'ABSENT', 'FF', 'F']:
                grade = 'F'

            # UPSERT Marks
            mark_record = Marks.query.filter_by(student_id=student.id, subject_id=subject_id).first()
            if not mark_record:
                mark_record = Marks(student_id=student.id, subject_id=subject_id)
                db.session.add(mark_record)

            mark_record.marks_obtained = marks_obtained
            mark_record.max_marks = max_marks
            mark_record.grade = grade
            
    # Final Commit for the loop
    db.session.commit()
