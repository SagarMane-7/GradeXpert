import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'data.sqlite'))

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        # Check if name column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'name' not in columns:
            print("Migrating Database: Adding 'name'...")
            cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR(150)")
        if 'registration_id' not in columns:
            print("Migrating Database: Adding 'registration_id'...")
            cursor.execute("ALTER TABLE users ADD COLUMN registration_id VARCHAR(50)")
        if 'institute' not in columns:
            print("Migrating Database: Adding 'institute'...")
            cursor.execute("ALTER TABLE users ADD COLUMN institute VARCHAR(255)")
            
        print("Database Migration Complete!")
        conn.commit()
    else:
        print("Table 'users' does not exist yet. SQLAlchemy will auto-create it with the new schema on boot.")
    
    conn.close()
else:
    print(f"No DB found at {db_path}. SQLAlchemy will auto-create it on boot.")
