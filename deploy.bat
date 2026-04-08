@echo off
REM Quick Deployment Prep Script for SATYA-SETU

echo ========================================
echo SATYA-SETU - Deployment Preparation
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
) else (
    echo Git repository already initialized.
    echo.
)

REM Add all files
echo Adding all files to git...
git add .
echo.

REM Ask for commit message
set /p message="Enter commit message (default: 'Deploy to Render'): "
if "%message%"=="" set message=Deploy to Render

echo Committing changes...
git commit -m "%message%"
echo.

REM Show git status
echo Current Git Status:
git status
echo.

echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. Create a GitHub repository at https://github.com/new
echo.
echo 2. Add the remote repository (replace OWNER/REPO):
echo    git remote add origin https://github.com/OWNER/REPO.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Go to https://render.com and create a new Web Service
echo    - Connect to your GitHub repository
echo    - Build Command: pip install -r requirements-deploy.txt
echo    - Start Command: cd backend ^&^& gunicorn app:app
echo.
echo 4. Set Environment Variables in Render Dashboard:
echo    DATABASE_URL, JWT_SECRET, EMAIL_SENDER, EMAIL_PASSWORD
echo.
echo 5. Deploy and enjoy!
echo.
pause
