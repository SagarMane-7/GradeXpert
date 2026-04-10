import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        engine = db.engine
        
        with engine.connect() as conn:
            print("Connected to database defined by app.y!")
            
            # Check existing columns using native approach instead of raw SQL
            # However, text executes raw SQL across Postgres/SQLite easily for simple ADD COLUMN.
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(150)"))
                print("Added column: name")
            except Exception as e:
                pass # Usually implies column already exists
                
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN registration_id VARCHAR(50)"))
                print("Added column: registration_id")
            except Exception as e:
                pass
                
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN institute VARCHAR(255)"))
                print("Added column: institute")
            except Exception as e:
                pass
                
            conn.commit()
            print("Database Migration Check Complete.")

if __name__ == "__main__":
    update_schema()
