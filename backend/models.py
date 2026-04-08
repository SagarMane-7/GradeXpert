from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'hod', 'faculty'
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True) # Null for Admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LedgerUpload(db.Model):
    __tablename__ = 'ledger_uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    academic_year = db.Column(db.String(20))
    semester = db.Column(db.String(10))
    total_students = db.Column(db.Integer)
    pass_count = db.Column(db.Integer)
    fail_count = db.Column(db.Integer)

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student', backref='branch_ref', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    seat_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    academic_year = db.Column(db.String(20))
    marks = db.relationship('Marks', backref='student', lazy=True)
    # Link to specific upload batch
    upload_id = db.Column(db.Integer, db.ForeignKey('ledger_uploads.id'), nullable=True)

class Marks(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, default=100.0)
    grade = db.Column(db.String(5))
