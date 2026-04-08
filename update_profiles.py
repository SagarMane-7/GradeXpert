import os
import re

d = r'c:\Users\ADI\OneDrive\Desktop\frontend sppu - Copy (2)\frontend\templates'
rep = r'''            <div class="user-profile">
                <div class="avatar">A</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 0.9rem;">Admin User</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Administrator</div>
                </div>
                <i class="fa-solid fa-chevron-right" style="font-size: 0.8rem; color: var(--text-secondary);"></i>
            </div>'''
            
p = re.compile(r'[ \t]*<div class="user-profile">.*?(?=</aside>)', re.DOTALL)

for f in os.listdir(d):
    if f.endswith('.html'):
        path = os.path.join(d, f)
        with open(path, 'r', encoding='utf-8') as file:
            c = file.read()
        
        c_new = p.sub(rep + '\n        ', c)
        
        if c != c_new:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(c_new)
            print(f'Updated {f}')
print('Done')
