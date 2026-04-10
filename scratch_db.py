import os
import sys
import sqlite3

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'data.sqlite'))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get users
cursor.execute("SELECT * FROM users")
print("USERS:", cursor.fetchall())

# Get branches
cursor.execute("SELECT * FROM branches")
print("BRANCHES:", cursor.fetchall())

conn.close()
