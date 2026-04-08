import sys
import os

# Put backend dir in path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.ledger_parser import parse_sppu_ledger, generate_excel_from_data

pdf_path = os.path.join("uploads", "S.Y.B.Tech - ETE - 7 - ConsolidateGazette.pdf")
output_path = os.path.join("generated", "test_report.xlsx")

print("Parsing PDF...")
students = parse_sppu_ledger(pdf_path)
print(f"Extracted {len(students)} students.")
if students:
    print("Sample student:", students[0])

print("Generating Excel...")
df = generate_excel_from_data(students, output_path)
print("Excel columns:", df.columns.tolist() if not df.empty else "Empty DataFrame")
print("Done.")
