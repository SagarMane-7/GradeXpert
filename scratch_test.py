import os
import sys

# Ensure backend works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.ledger_parser import parse_sppu_ledger
import time
import glob

# Find all pdfs
pdf_files = glob.glob(os.path.join(os.path.dirname(__file__), 'uploads', '*.pdf'))

found = False
for pdf_path in pdf_files:
    try:
        students = parse_sppu_ledger(pdf_path)
        for s in students:
            if s['seat_no'] == 'S240502333' or 'Chinmay' in s['name']:
                print(f"FOUND IN {pdf_path}!")
                print(f"Name: {s['name']}, Status: {s['status']}, SGPA: {s['sgpa']}")
                for sub in s['subjects_list']:
                    if sub['status'] == 'Fail':
                        print(f"FAILED SUBJECT: {sub['subject_code']} - {sub['subject_name']} -> Grade: {sub['grade']}, Marks: {sub['marks']}")
                found = True
        
        if found: break
    except Exception as e:
        print(f"Error parsing {pdf_path}: {e}")

if not found:
    print("Student not found anywhere!")
