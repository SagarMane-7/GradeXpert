# 🎓 SATYA-SETU: SPPU Academic Intelligence Dashboard & Ledger Parser

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-green)
![Pandas](https://img.shields.io/badge/Data-Pandas-red)
![License](https://img.shields.io/badge/License-MIT-purple)

Welcome to **SATYA-SETU**, an intelligent, structured, and role-based Academic Intelligence Dashboard designed specifically for SPPU (Savitribai Phule Pune University). 

This README provides the **Ultimate Step-by-Step Guide** to open, configure, and seamlessly run this project in **Visual Studio Code (VS Code)** without any bugs or dependency issues.

---

## 🛠️ The Technology Stack & Dependencies

To guarantee this project runs without any bugs, the environment relies on the exact libraries listed in your `requirements.txt`. Here are the core engines used:

| Component | Library/Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Core** | `flask`, `werkzeug` | Powers the local server API and renders the HTML templates. |
| **Data Parsing** | `pdfplumber` | Reads the complicated layout of SPPU PDF files safely. |
| **Data Analysis** | `pandas`, `openpyxl` | Analyzes student marks, converts them into Excel sheets, and tracks performance. |
| **Database** | `flask-sqlalchemy` | Local SQLite database mapper to store login credentials and upload history. |
| **Security** | `flask-jwt-extended`, `flask-cors` | Secure login workflows and token management. |

---

## 🚀 How to Run the Project in VS Code (Step-by-Step Plan)

Follow these exact instructions to launch SATYA-SETU perfectly on your local machine using Visual Studio Code.

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Go to **File** > **Open Folder...** (or press `Ctrl+K` then `Ctrl+O`).
3. Select the folder named `frontend sppu` (or `frontend sppu - Copy (2)` depending on your current directory name), and click **Select Folder**.

### Step 2: Open a VS Code Terminal
1. In the top VS Code menu bar, click on **Terminal** > **New Terminal** (or press `` Ctrl + ` ``).
2. Ensure you are at the root level of your project directory in this terminal.

### Step 3: Create a Virtual Environment (Crucial against Bugs)
To prevent your global Python packages from crashing this app, always use a virtual environment. In the terminal, type:

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment
Activate the environment so that VS Code knows where to install the packages.

**For Windows (Command Prompt / PowerShell):**
```bash
.venv\Scripts\activate
```
*(You will see `(.venv)` prefix your terminal bracket when it works).*

### Step 5: Install Required Dependencies
With the virtual environment active, run the following command to download all exact dependencies needed to run the app cleanly:

```bash
pip install -r requirements.txt
```
*Wait a few seconds for all packages (like Flask, Pandas, pdfplumber) to install successfully.*

### Step 6: Configure Security Variables
The application needs a secure key for login functionality. 
1. Look at your file explorer on the left sidebar in VS Code.
2. If there is no `.env` file, click **New File**, name it `.env`.
3. Add the following line to the `.env` file and save it (`Ctrl+S`):
```env
JWT_SECRET=super-secret-sppu-key-2026
```

### Step 7: Launch the Application
Start the backend server which automatically serves your database and dashboard interfaces.

1. First, navigate into the backend folder:
```bash
cd backend
```
2. Next, securely run the Flask server:
```bash
python app.py
```

### Step 8: View the Application
Once the terminal reads `* Running on http://127.0.0.1:5000`, your server is successfully active!
1. Hold `Ctrl` and **click the link** `http://127.0.0.1:5000` in the VS Code terminal.
2. Your default web browser will open SATYA-SETU locally.
3. Login using the default administrator credentials:
   - **Username:** `admin`
   - **Password:** `admin`

---

## 🛑 Troubleshooting & Maintenance Guide

- **Terminal says `python is not recognized`**: You must install Python from `python.org` and ensure "Add Python to PATH" is checked during installation.
- **Port 5000 is already in use**: Another app is using this port. Close other background Python tasks, or configure Flask to use a different port like `5001`.
- **VS Code Pylance/Import Warnings**: While the app runs fine, VS Code might show yellow squiggly lines. Press `Ctrl+Shift+P`, type `Python: Select Interpreter`, and select the one located in your `.venv` directory to sync the IDE with your libraries.

---

## 🔐 System Architecture Flow

1. **Authentication:** The `admin` user logs in through the frontend `index.html`.
2. **Uploading:** A PDF ledger is securely passed to `backend/services/ledger_parser.py`.
3. **Structuring:** `pdfplumber` breaks down tables while skipping headers/footers, and `pandas` calculates class averages and fails.
4. **Caching:** The dashboard components load dynamic SVG and Chart.js canvases based on immediate, exact SQLite backend reads.
5. **Print Mode**: A custom engineered `Ctrl+P` export layout hides the web layout and scales analytics perfectly to A4 PDF exports.
