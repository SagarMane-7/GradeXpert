import pdfplumber
import os

pdf_dir = r"d:\Insightix\uploads"
for f in os.listdir(pdf_dir):
    if f.endswith('.pdf'):
        with pdfplumber.open(os.path.join(pdf_dir, f)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if "Analog Circuit Design" in line or "2303102" in line:
                        print(f"FOUND IN {f}: {line}")
                        if i+1 < len(lines):
                            print(f"NEXT LINE: {lines[i+1]}")
