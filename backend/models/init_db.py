"""
GradeXpert - SQLite Database Initialization
Creates all tables and seeds default data.
"""
import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gradexpert.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'faculty',
    branch_id INTEGER,
    name TEXT,
    registration_id TEXT,
    institute TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ledger_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER NOT NULL,
    academic_year TEXT,
    semester TEXT,
    total_students INTEGER DEFAULT 0,
    pass_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    branch_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    UNIQUE(name, branch_id, semester)
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seat_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    branch_id INTEGER,
    academic_year TEXT,
    upload_id INTEGER,
    sgpa REAL,
    status TEXT,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
    FOREIGN KEY (upload_id) REFERENCES ledger_uploads(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    marks_obtained REAL NOT NULL,
    max_marks REAL DEFAULT 100.0,
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(student_id, subject_id)
);
"""

DEFAULT_BRANCHES = [
    'Computer Engineering',
    'Information Technology',
    'Electronics and Telecommunication',
    'Artificial Intelligence and Data Science',
    'Electronics and Computer Engineering'
]

def init_database():
    """Initialize the database with schema and seed data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")

        # Create tables
        cursor.executescript(SCHEMA)

        # Seed default branches
        for branch_name in DEFAULT_BRANCHES:
            cursor.execute(
                "INSERT OR IGNORE INTO branches (name) VALUES (?)",
                (branch_name,)
            )

        # Seed default admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, name, registration_id, institute) VALUES (?, ?, ?, ?, ?, ?)",
                ('admin', password_hash, 'admin', 'Administrator', 'ADMIN001', 'PICT')
            )
            print("[INIT] Default admin user created: admin / admin123")

        conn.commit()
        print(f"[INIT] Database verified at: {DB_PATH}")
    except Exception as e:
        print(f"[INIT] Database initialization failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
