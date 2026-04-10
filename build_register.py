import re

with open('frontend/templates/register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace title
content = content.replace('<title>Academic Portal Login</title>', '<title>Academic Portal Registration</title>')
content = content.replace('<h2>Welcome Back</h2>', '<h2>Register Account</h2>')
content = content.replace('<p>Sign in to access result ledgers & analytics</p>', '<p>Create your new secure account</p>')

# The form block replacement
form_html = '''<form id="registerForm" onsubmit="handleRegister(event)">
                <div class="input-group">
                    <label>Full Name</label>
                    <input type="text" id="name" placeholder="Enter your full name" required autocomplete="name">
                    <i class="fa-regular fa-user input-icon"></i>
                </div>

                <div class="input-group">
                    <label>Registration ID</label>
                    <input type="text" id="registration_id" placeholder="e.g., TECH12345" required>
                    <i class="fa-solid fa-id-card input-icon"></i>
                </div>

                <div class="input-group">
                    <label>Institute Name</label>
                    <input type="text" id="institute" value="SCTR'S Pune Institute of Computer Technology" readonly style="background-color:#f1f5f9; color:#64748b; cursor:not-allowed;">
                    <i class="fa-solid fa-university input-icon"></i>
                </div>

                <div class="input-group">
                    <label>Department</label>
                    <div style="position: relative;">
                        <select id="department" required style="width: 100%; padding: 12px 16px 12px 42px; border: 1.5px solid var(--surface-border); border-radius: 10px; font-size: 14.5px; background: rgba(255, 255, 255, 0.8); color: var(--text-main); font-weight: 500; appearance: none; transition: all 0.3s ease;">
                            <option value="">Select your department</option>
                            <option value="Computer Engineering">Computer Engineering</option>
                            <option value="Information Technology">Information Technology</option>
                            <option value="Electronics and Telecommunication Engineering">Electronics and Telecommunication Engineering</option>
                            <option value="Artificial Intelligence and Data Science">Artificial Intelligence and Data Science</option>
                            <option value="Electronics and Computer Engineering">Electronics and Computer Engineering</option>
                        </select>
                        <i class="fa-solid fa-building input-icon"></i>
                        <i class="fa-solid fa-chevron-down" style="position: absolute; right: 16px; top: 16px; color: #94a3b8; pointer-events: none;"></i>
                    </div>
                </div>

                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="password" placeholder="Create a password" required>
                    <i class="fa-solid fa-lock input-icon"></i>
                    <i class="fa-solid fa-eye-slash toggle-eye" onclick="togglePwd('password', this)" style="position: absolute; right: 16px; top: 40px; color: #94a3b8; cursor: pointer;"></i>
                </div>

                <div class="input-group">
                    <label>Confirm Password</label>
                    <input type="password" id="confirm_password" placeholder="Confirm your password" required>
                    <i class="fa-solid fa-lock input-icon"></i>
                    <i class="fa-solid fa-eye-slash toggle-eye" onclick="togglePwd('confirm_password', this)" style="position: absolute; right: 16px; top: 40px; color: #94a3b8; cursor: pointer;"></i>
                </div>

                <button type="submit" class="btn-login" id="registerBtn">
                    <span id="btnText">Create Account</span>
                    <i id="btnIcon" class="fa-solid fa-user-plus" style="font-size: 14px; margin-left: 4px;"></i>
                    <div class="loader" id="loader"></div>
                </button>
            </form>
            
            <p style="text-align: center; margin-top: 25px; font-size: 14px; color: var(--text-muted);">
                Already have an account? 
                <a href="index.html" style="color: var(--primary); text-decoration: none; font-weight: 600;">Sign In</a>
            </p>'''

old_form_start = content.find('<form id="loginForm"')
end_p = content.find('</div>\n    </div>\n\n    <script>')

# Replace the body form section
content = content[:old_form_start] + form_html + '\n        ' + content[end_p:]

# Add JS logic instead of login function
js_logic = '''
        function togglePwd(id, icon) {
            const input = document.getElementById(id);
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        }

        async function handleRegister(e) {
            e.preventDefault();

            const name = document.getElementById("name").value.trim();
            const registration_id = document.getElementById("registration_id").value.trim();
            const institute = document.getElementById("institute").value.trim();
            const department = document.getElementById("department").value;
            const password = document.getElementById("password").value;
            const confirm_password = document.getElementById("confirm_password").value;

            if (password !== confirm_password) {
                showToast("Passwords do not match!");
                return;
            }

            const btnText = document.getElementById("btnText");
            const btnIcon = document.getElementById("btnIcon");
            const loader = document.getElementById("loader");
            const registerBtn = document.getElementById("registerBtn");

            registerBtn.disabled = true;
            btnText.style.display = "none";
            btnIcon.style.display = "none";
            loader.style.display = "block";

            try {
                const res = await fetch(`${BASE_URL}/api/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, registration_id, institute, department, password })
                });

                const data = await res.json();

                if (!res.ok) {
                    showToast(data.error || "Failed to register.");
                    resetBtn();
                    return;
                }

                // Success! Redirect to login page
                showToast("Registration successful! Redirecting...");
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 1500);

            } catch (err) {
                console.error("Registration Error:", err);
                showToast("Server connection error.");
                resetBtn();
            }

            function resetBtn() {
                registerBtn.disabled = false;
                btnText.style.display = "inline";
                btnIcon.style.display = "inline";
                loader.style.display = "none";
            }
        }
'''

content = re.sub(r'async function handleLogin\(e\).*?(?=let toastTimeout;)', js_logic, content, flags=re.DOTALL)
with open('frontend/templates/register.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Register form created successfully!")
