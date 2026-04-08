import re

lines = [
    "2303203 * Analog Circuit Design --- --- --- --- 22/25 --- 19/25 41/50 82 1 A+ 9 9",
    "* Network Analysis and",
    "2303104 49/60 20/20 15/15 3/5 --- --- --- 87/100 87 2 A+ 9 18",
    "Synthesis",
    "* Network Analysis and",
    "2303104 --- --- --- --- 22/25 --- --- 22/25 88 1 A+ 9 9",
    "Synthesis",
    "* Electronics Skill",
    "2307201 --- --- --- --- 44/50 21/25 --- 65/75 86.67 2 A+ 9 18",
    "Development Lab"
]

for i, line in enumerate(lines):
    line = line.strip()
    subject_match = re.search(r'^[\*\s]*([0-9]{3,}[A-Z0-9_\(\)\-]*)\s*(.+)', line)
    
    if subject_match:
        code = subject_match.group(1)
        remaining_content = subject_match.group(2).strip()
        
        # Determine prefix and suffix names
        name_prefix = ""
        name_suffix = ""
        
        if i > 0:
            prev_line = lines[i-1].strip()
            # If prev line does not start with typical data identifiers
            if prev_line and not re.match(r'^(?:SEAT|Name|PROGRAM|PRN|SUB|[0-9]{3,})', prev_line, re.IGNORECASE):
                # We ALSO need to make sure the previous line wasn't the suffix of the prior subject...
                # actually, usually there's a '*' indicating a new subject name starts.
                # If it starts with '*', it is definitely a prefix!
                if prev_line.startswith('*') or not any(char.isdigit() for char in prev_line):
                    name_prefix = prev_line

        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            # If next line looks like text and not part of the next block
            if next_line and not re.match(r'^(?:SEAT|Name|PROGRAM|PRN|SUB|\*|[0-9]{3,})', next_line, re.IGNORECASE):
                name_suffix = next_line
                
        # Main regex logic
        mark_start = re.search(r'\s+(\d+/\d+|[A-Za-z]+/\d+|---|AB|Ab|FF|\b\d+\b)\s+', " " + remaining_content)
        if mark_start:
            name_core = remaining_content[:mark_start.start()].strip()
        else:
            name_core = "" # fallback
            
        full_name = f"{name_prefix} {name_core} {name_suffix}".strip()
        if full_name.startswith('*'): full_name = full_name[1:].strip()
        
        print(f"Code: {code} | Name: {full_name} | Prefix: '{name_prefix}' | Core: '{name_core}' | Suffix: '{name_suffix}'")
