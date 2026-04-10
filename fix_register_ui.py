import re

with open('frontend/templates/register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The form block replacement
form_html = '''<form id="registerForm" onsubmit="handleRegister(event)">
                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Full Name</label>
                    <input type="text" id="name" class="form-control" placeholder="Enter your full name" required autocomplete="name">
                    <i class="fa-regular fa-user input-icon" style="top: 38px;"></i>
                </div>

                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Registration ID</label>
                    <input type="text" id="registration_id" class="form-control" placeholder="e.g., TECH12345" required>
                    <i class="fa-solid fa-id-card input-icon" style="top: 38px;"></i>
                </div>

                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Institute Name</label>
                    <input type="text" id="institute" class="form-control" value="SCTR'S Pune Institute of Computer Technology" readonly style="background-color:#f1f5f9; color:#64748b; cursor:not-allowed;">
                    <i class="fa-solid fa-university input-icon" style="top: 38px;"></i>
                </div>

                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Department</label>
                    <div style="position: relative;">
                        <select id="department" class="form-control" required style="appearance: none; cursor: pointer;">
                            <option value="">Select your department</option>
                            <option value="Computer Engineering">Computer Engineering</option>
                            <option value="Information Technology">Information Technology</option>
                            <option value="Electronics and Telecommunication Engineering">Electronics and Telecommunication Engineering</option>
                            <option value="Artificial Intelligence and Data Science">Artificial Intelligence and Data Science</option>
                            <option value="Electronics and Computer Engineering">Electronics and Computer Engineering</option>
                        </select>
                        <i class="fa-solid fa-building input-icon" style="top: 50%;"></i>
                        <i class="fa-solid fa-chevron-down" style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none;"></i>
                    </div>
                </div>

                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Password</label>
                    <div style="position: relative;">
                        <input type="password" id="password" class="form-control" placeholder="Create a password" required>
                        <i class="fa-solid fa-lock input-icon" style="top: 50%;"></i>
                        <i class="fa-solid fa-eye-slash toggle-eye" onclick="togglePwd('password', this)" style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: #94a3b8; cursor: pointer; z-index: 10;"></i>
                    </div>
                </div>

                <div class="input-group">
                    <label style="display:block; margin-bottom: 5px; font-size: 13px; font-weight: 500; color: var(--text-muted);">Confirm Password</label>
                    <div style="position: relative;">
                        <input type="password" id="confirm_password" class="form-control" placeholder="Confirm your password" required>
                        <i class="fa-solid fa-lock input-icon" style="top: 50%;"></i>
                        <i class="fa-solid fa-eye-slash toggle-eye" onclick="togglePwd('confirm_password', this)" style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: #94a3b8; cursor: pointer; z-index: 10;"></i>
                    </div>
                </div>

                <button type="submit" class="btn-login" id="registerBtn">
                    <span id="btnText">Create Account</span>
                    <i id="btnIcon" class="fa-solid fa-user-plus" style="font-size: 14px; margin-left: 4px;"></i>
                    <div class="loader" id="loader"></div>
                </button>
            </form>'''

old_form_start = content.find('<form id="registerForm"')
end_p = content.find('</form>') + 7

# Replace the body form section
content = content[:old_form_start] + form_html + content[end_p:]

with open('frontend/templates/register.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Register form UI fixed!")
