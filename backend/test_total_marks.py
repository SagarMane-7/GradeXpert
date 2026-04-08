import re

text = "57/60 5/5 14/15 15/20 --- --- --- 91/100 91 3 O 10 30"
allowed_grades = {'O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'Ab', 'PP', 'NP', 'AP', 'AC', 'XX'}
parts = text.split()
grade = None
for p in reversed(parts):
    if p in allowed_grades:
        grade = p
        break

grade_idx = len(parts) - 1 - list(reversed(parts)).index(grade)
total_marks = parts[grade_idx - 3] if grade_idx >= 3 else ""

print(f"Parts: {parts}")
print(f"Grade: {grade}")
print(f"Grade idx: {grade_idx}")
print(f"Total marks parsed: {total_marks}")

components = []
for p in parts[:max(0, grade_idx - 3)]:
    if '/' in p and p[0].isdigit():
        components.append(p)
print(f"Components: {components}")

is_theory = False
try:
    if '/' in total_marks and int(total_marks.split('/')[1]) == 100:
        is_theory = True
except Exception as e: 
    print(f"Error checking is_theory: {e}")

print(f"is_theory: {is_theory}")

if not is_theory:
    print("If not theory, this maps to:")
    tw_count = 0
    pr_count = 0
    insem_count = 0
    ese_count = 0
    or_count = 0
    cie_count = 0
    for p in components:
        parts_frac = p.split('/')
        num = int(parts_frac[0])
        denom = int(parts_frac[1])
        if denom >= 60: 
            comp_name = 'ESE' if ese_count == 0 else 'ESE2'
            ese_count += 1
        elif denom == 50: 
            comp_name = 'PR' if pr_count == 0 else 'CIE'
            pr_count += 1
        elif denom == 30 or denom == 15:
            comp_name = 'INSEM' if insem_count == 0 else 'INSEM2'
            insem_count += 1
        elif denom == 25:
            comp_name = 'TW' if tw_count == 0 else 'TW2'
            tw_count += 1
        elif denom == 20:
            comp_name = 'OR' if or_count == 0 else 'OR2'
            or_count += 1
        elif denom == 10 or denom == 5:
            comp_name = 'CIE' if cie_count == 0 else 'ATTD'
            cie_count += 1
        else:
            comp_name = f'COMP_{denom}'
        print(f"{p} ({denom}) -> {comp_name}")
