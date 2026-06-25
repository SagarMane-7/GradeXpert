-- ============================================================
-- GradeXpert - PostgreSQL Database Schema & Table Documentation
-- Compatible with Neon PostgreSQL, Supabase, Render & Local Postgres
-- ============================================================

-- ------------------------------------------------------------
-- 1. Branches Table
-- Purpose: Stores academic engineering departments (e.g. Computer Engineering, IT, ENTC).
-- Relationships: Referenced by users, subjects, and students.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing unique branch identifier
    name VARCHAR(100) UNIQUE NOT NULL   -- Department name (must be unique)
);

-- ------------------------------------------------------------
-- 2. Users Table
-- Purpose: Stores user credentials for faculty members and system administrators.
-- Relationships: Links to branches via branch_id; referenced by ledger_uploads.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                       -- Auto-incrementing user ID
    username VARCHAR(80) UNIQUE NOT NULL,        -- Faculty Registration ID / Username
    password_hash VARCHAR(256) NOT NULL,         -- Bcrypt hashed password for secure login
    role VARCHAR(20) NOT NULL DEFAULT 'faculty', -- Role permissions ('admin' or 'faculty')
    branch_id INT REFERENCES branches(id) ON DELETE SET NULL, -- Assigned department ID
    name VARCHAR(150),                           -- Full name of faculty/admin
    registration_id VARCHAR(50),                 -- Employee / Faculty ID
    institute VARCHAR(255),                      -- College / Institute name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Registration timestamp
);

-- ------------------------------------------------------------
-- 3. Ledger Uploads Table
-- Purpose: Tracks every SPPU PDF result ledger file uploaded by teachers.
-- Relationships: Foreign key to users(id); referenced by students.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_uploads (
    id SERIAL PRIMARY KEY,                              -- Upload session ID
    filename VARCHAR(255) NOT NULL,                     -- Original PDF file name
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Upload timestamp
    uploaded_by INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- User who uploaded PDF
    academic_year VARCHAR(20),                          -- e.g. "2024-2025"
    semester VARCHAR(10),                               -- e.g. "Semester 1"
    total_students INT DEFAULT 0,                       -- Total parsed students in batch
    pass_count INT DEFAULT 0,                           -- Number of passed students in batch
    fail_count INT DEFAULT 0                            -- Number of failed students in batch
);

-- ------------------------------------------------------------
-- 4. Subjects Table
-- Purpose: Stores subject master data per branch and semester (e.g., DBMS, TOC).
-- Relationships: Foreign key to branches(id); referenced by marks.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,                  -- Unique subject ID
    name VARCHAR(150) NOT NULL,             -- Subject title (e.g. Database Management Systems)
    branch_id INT NOT NULL REFERENCES branches(id) ON DELETE CASCADE, -- Branch offering this subject
    semester INT NOT NULL,                  -- Semester number (1 to 8)
    CONSTRAINT unique_subject UNIQUE (name, branch_id, semester) -- Unique constraint per branch/sem
);

-- ------------------------------------------------------------
-- 5. Students Table
-- Purpose: Stores individual student result records parsed from PDF ledgers.
-- Relationships: Foreign keys to branches(id) and ledger_uploads(id); referenced by marks.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,               -- Internal student ID
    seat_no VARCHAR(50) UNIQUE NOT NULL, -- SPPU Seat Number / PRN (unique per student)
    name VARCHAR(150) NOT NULL,          -- Full student name
    branch_id INT REFERENCES branches(id) ON DELETE SET NULL, -- Student's branch ID
    academic_year VARCHAR(20),           -- Academic batch year
    upload_id INT REFERENCES ledger_uploads(id) ON DELETE SET NULL, -- Upload batch source
    sgpa DOUBLE PRECISION,               -- Semester Grade Point Average (e.g. 8.75)
    status VARCHAR(20)                   -- Result status ('Pass', 'Fail', 'ATKT')
);

-- ------------------------------------------------------------
-- 6. Marks Table
-- Purpose: Stores granular subject-wise marks, max marks, and letter grades for students.
-- Relationships: Foreign keys to students(id) and subjects(id).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,                   -- Unique mark entry ID
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE, -- Student receiving marks
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE, -- Subject evaluated
    marks_obtained DOUBLE PRECISION NOT NULL, -- Score achieved by student
    max_marks DOUBLE PRECISION DEFAULT 100.0, -- Maximum total score (100=Theory, <100=Practical/Oral)
    grade VARCHAR(5),                         -- Letter grade ('O', 'A+', 'A', 'B', 'F', etc.)
    CONSTRAINT unique_marks UNIQUE (student_id, subject_id) -- One mark entry per student per subject
);

-- ------------------------------------------------------------
-- Seed Default Engineering Branches
-- ------------------------------------------------------------
INSERT INTO branches (name) VALUES 
    ('Computer Engineering'),
    ('Information Technology'),
    ('Electronics and Telecommunication'),
    ('Artificial Intelligence and Data Science'),
    ('Electronics and Computer Engineering')
ON CONFLICT (name) DO NOTHING;
