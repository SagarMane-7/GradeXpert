import re

lines = [
    "PROGRAM : SY BTech-ETE",
    "SEAT NO : S240502013     Name : Ritika Sunil Badiger        Mother : Manjula         PRN : F24ET278",
    "2303101 * Signals and Systems 47/60 10/20 13/15 3/5 --- --- --- 73/100 73 3 A 8 24",
    "2303102 * Analog Circuit Design 44/60 12/20 12/15 4/5 --- --- --- 72/100 72 3 A 8 24",
    "2303203 * Analog Circuit Design --- --- --- --- 22/25 --- 19/25 41/50 82 1 A+ 9 9",
    "SGPA : 8.77                 Total Earned Credits: 22"
]

current_branch = "Unknown"
for line in lines:
    line = line.strip()
    print("LINE:", line)
    
    if "PROGRAM :" in line:
        branch_match = re.search(r"PROGRAM\s*:\s*(.+)", line, re.IGNORECASE)
        if branch_match:
            current_branch = branch_match.group(1).strip()
            print("FOUND BRANCH:", current_branch)
            
    seat_match = re.search(r"SEAT NO\s*:\s*([A-Z0-9]+)", line, re.IGNORECASE)
    if seat_match:
        print("FOUND SEAT NO:", seat_match.group(1))
        
        # Name
        name_match = re.search(r"Name\s*:\s*([^:]+?)(?=\s+Mother\s*:|$)", line, re.IGNORECASE)
        if name_match:
            print("FOUND NAME:", name_match.group(1).strip())
            
        # Mother
        mother_match = re.search(r"Mother\s*:\s*([^:]+?)(?=\s+PRN\s*:|$)", line, re.IGNORECASE)
        if mother_match:
            print("FOUND MOTHER:", mother_match.group(1).strip())
            
        # PRN
        prn_match = re.search(r"PRN\s*:\s*([A-Z0-9]+)", line, re.IGNORECASE)
        if prn_match:
            print("FOUND PRN:", prn_match.group(1).strip())
            
    # SGPA
    sgpa_match = re.search(r"SGPA\s*:\s*([\d\.]+)", line, re.IGNORECASE)
    if sgpa_match:
        print("FOUND SGPA:", float(sgpa_match.group(1)))
        
    # Subjects
    # Line pattern: CODE * NAME M1 M2 M3 ... 
    subject_match = re.search(r'^([A-Z0-9]{5,})\s*[\*\s]*(.+)', line)
    if subject_match:
        code = subject_match.group(1)
        rest = subject_match.group(2)
        print("POSSIBLE SUBJECT:", code, rest)
        
        # Look for the grade backward
        allowed_grades = {'O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'Ab', 'PP', 'NP', 'AP', 'AC', 'XX'}
        parts = rest.split()
        found_grade = None
        for i in range(len(parts)-1, -1, -1):
            if parts[i] in allowed_grades:
                found_grade = parts[i]
                break
                
        if found_grade:
            print("FOUND GRADE:", found_grade)
            # Find subject name by trimming from the first mark-looking thing
            # Marks can be "47/60", "---", "73", etc.
            # We can use regex to split where the scores start
            scores_start = re.search(r'\s+((?:---)|(?:\d+/\d+)|\b\d+\b)', rest)
            if scores_start:
                name = rest[:scores_start.start()].strip()
                # remove leading * if present
                if name.startswith('*'):
                    name = name[1:].strip()
                print("FOUND SUBJECT NAME:", name)
