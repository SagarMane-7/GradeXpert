import os
import re

base_path = r"c:\Users\Sagar\Downloads\Insightix\Insightix"
frontend_path = os.path.join(base_path, 'frontend')

# We use the requested direct string or local condition.
# "first make it compatible for local hosting and then for for deployment on render"
# So let's use a condition that works for both.
base_url_snippet = 'const BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://127.0.0.1:10000" : "https://gradexpert.onrender.com";\n'

for root, dirs, files in os.walk(frontend_path):
    for f in files:
        if f.endswith('.html') or f.endswith('.js'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            original_content = content
            
            # For fetching
            content = re.sub(r'fetch\([\'"]/api/', r'fetch(`${BASE_URL}/api/', content)
            content = re.sub(r'fetch\(`/api/', r'fetch(`${BASE_URL}/api/', content)
            
            # For window.location
            content = re.sub(r'location\.href\s*=\s*[\'"]/api/', r'location.href = `${BASE_URL}/api/', content)
            content = re.sub(r'location\.href\s*=\s*`/api/', r'location.href = `${BASE_URL}/api/', content)
            
            # special case in upload.html and dashboard.html
            content = content.replace("onclick=\"window.location.href='/api/report/download?jwt=' + localStorage.getItem('token')\"", 
                                      "onclick=\"window.location.href=`${BASE_URL}/api/report/download?jwt=` + localStorage.getItem('token')\"")
            
            content = content.replace("window.location.href='/api/report/download?' + p.toString()",
                                      "window.location.href=`${BASE_URL}/api/report/download?` + p.toString()")
                                      
            
            if f == 'main.js':
                content = re.sub(r"const API_BASE = .*;", f"{base_url_snippet.strip()}\nconst API_BASE = `${{BASE_URL}}/api`;", content)
            elif f.endswith('.html') and content != original_content:
                # only add to html files if we actually replaced fetches / locations
                if 'const BASE_URL =' not in content:
                    content = content.replace('<script>', f'<script>\n        {base_url_snippet}')
            elif f.endswith('.js') and f != 'main.js' and content != original_content:
                if 'const BASE_URL =' not in content:
                    content = base_url_snippet + '\n' + content

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                    print(f"Updated {filepath}")
                
# Remove .venv from git
gitignore_path = os.path.join(base_path, '.gitignore')
has_venv = False
if os.path.exists(gitignore_path):
    with open(gitignore_path, 'r', encoding='utf-8') as file:
        ig_content = file.read()
    if '.venv' not in ig_content:
        with open(gitignore_path, 'a', encoding='utf-8') as file:
            file.write('\n.venv\n')
        print("Added .venv to .gitignore")
else:
    with open(gitignore_path, 'w', encoding='utf-8') as file:
        file.write('.venv\n')
    print("Created .gitignore with .venv")
