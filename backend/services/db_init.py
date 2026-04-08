from models import db, Branch, Student, Subject, User
from werkzeug.security import generate_password_hash

def init_db():
    """Pre-populate DB with branches and default Admin"""
    
    # 1. Seed Branches
    if Branch.query.count() == 0:
        branches = [
            "Computer Engineering",
            "Information Technology",
            "Electronics and Telecommunication",
            "Artificial Intelligence and Data Science"
        ]
        for b_name in branches:
            db.session.add(Branch(name=b_name))
        db.session.commit()
        print("Initialized Branches.")

    # 2. Seed Admin User
    if User.query.filter_by(role='admin').count() == 0:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Initialized Admin User: admin / admin123")
