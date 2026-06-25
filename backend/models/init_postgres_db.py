"""
GradeXpert - PostgreSQL Database Initialization Script
Connects to PostgreSQL database (Neon, Supabase, Render, or Local) and initializes tables & seed data.
"""

import os
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
except ImportError:
    pass

# Get PostgreSQL Connection String from Environment Variable or fallback
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql://neondb_owner:npg_8iXqLnGYWAVw@ep-mute-feather-axz53izu.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require'
)

SCHEMA_POSTGRES = """
-- 1. Branches Table (Engineering departments)
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Users Table (Faculty & Admins)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'faculty',
    branch_id INT REFERENCES branches(id) ON DELETE SET NULL,
    name VARCHAR(150),
    registration_id VARCHAR(50),
    institute VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Ledger Uploads Table (PDF Ledger Upload History)
CREATE TABLE IF NOT EXISTS ledger_uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    academic_year VARCHAR(20),
    semester VARCHAR(10),
    total_students INT DEFAULT 0,
    pass_count INT DEFAULT 0,
    fail_count INT DEFAULT 0
);

-- 4. Subjects Table (Course Master Catalog)
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    branch_id INT NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    semester INT NOT NULL,
    CONSTRAINT unique_subject UNIQUE (name, branch_id, semester)
);

-- 5. Students Table (Parsed Student Result Profiles)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    seat_no VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    branch_id INT REFERENCES branches(id) ON DELETE SET NULL,
    academic_year VARCHAR(20),
    upload_id INT REFERENCES ledger_uploads(id) ON DELETE SET NULL,
    sgpa DOUBLE PRECISION,
    status VARCHAR(20)
);

-- 6. Marks Table (Detailed Subject Scores & Grades)
CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    marks_obtained DOUBLE PRECISION NOT NULL,
    max_marks DOUBLE PRECISION DEFAULT 100.0,
    grade VARCHAR(5),
    CONSTRAINT unique_marks UNIQUE (student_id, subject_id)
);
"""

DEFAULT_BRANCHES = [
    'Computer Engineering',
    'Information Technology',
    'Electronics and Telecommunication',
    'Artificial Intelligence and Data Science',
    'Electronics and Computer Engineering'
]

def get_pg_db():
    return psycopg2.connect(DATABASE_URL)

def init_pg_database():
    """Execute schema creation and seed data on PostgreSQL."""
    try:
        conn = get_pg_db()
        cursor = conn.cursor()

        # Execute schema DDL
        cursor.execute(SCHEMA_POSTGRES)

        # Seed Branches
        for branch_name in DEFAULT_BRANCHES:
            cursor.execute(
                "INSERT INTO branches (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (branch_name,)
            )

        # Seed Default Admin User
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, name, registration_id, institute)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                ('admin', password_hash, 'admin', 'Administrator', 'ADMIN001', 'PICT')
            )
            print("[INIT] Created default admin user: admin / admin123")

        conn.commit()
        cursor.close()
        conn.close()
        print("[INIT] PostgreSQL Database successfully initialized!")
    except Exception as e:
        print(f"[INIT] Failed to initialize PostgreSQL DB: {e}")

if __name__ == '__main__':
    init_pg_database()
