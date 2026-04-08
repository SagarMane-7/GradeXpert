import re

lines = [
    "2303101 * Signals and Systems 47/60 10/20 13/15 3/5 --- --- --- 73/100 73 3 A 8 24",
    "2303104 * Network Analysis and Synthesis AB/60 AB/20 15/15 3/5 --- --- --- AB/100 87 2 A+ 9 18",
    "0311101 * Universal Human Values --- --- --- --- 22/25 --- --- 22/25 88 2 A+ 9 18",
    "304184 * Subject With Weird Marks 12/20 FF/20 --- 30/100 30 3 F 0 0"
]

for line in lines:
    subject_match = re.search(r'^[\*\s]*([0-9]{3,}[A-Z0-9_\(\)\-]*)\s*(.+)', line)
    if subject_match:
        code = subject_match.group(1)
        remaining_content = subject_match.group(2).strip()
        
        allowed_grades = {'O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'Ab', 'PP', 'NP', 'AP', 'AC', 'XX'}
        parts = remaining_content.split()
        found_grade = None
        for p in reversed(parts):
            if p in allowed_grades:
                found_grade = p
                break
                
        grade_idx = len(parts) - 1 - list(reversed(parts)).index(found_grade) if found_grade else -1
        total_marks = parts[grade_idx - 3] if grade_idx >= 3 else ""
        
        # Subject Name extraction
        mark_start = re.search(r'\s+(\d+/\d+|[a-zA-Z]+/\d+|---|AB|Ab|FF|\b\d+\b)\s+', " " + remaining_content)
        if mark_start:
            name = remaining_content[:mark_start.start()].strip()
        else:
            name = "FAIL"
            
        if name.startswith('*'): name = name[1:].strip()
            
        print(f"Code: {code}")
        print(f"Name: {name}")
        print(f"Total Marks: {total_marks}")
        print(f"Grade: {found_grade}")
        print(f"Combined: {total_marks} ({found_grade})")
        print("-" * 20)
