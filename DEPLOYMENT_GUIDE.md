# 🚀 SATYA-SETU Deployment Guide

## Option 1: Deploy to Render (Recommended for Flask Backend)

### Prerequisites
- GitHub account (push code to a repo)
- Render account (https://render.com)
- NeonDB PostgreSQL database (already configured)

### Steps:

#### 1. Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/satya-setu.git
git branch -M main
git push -u origin main
```

#### 2. Connect to Render
1. Go to https://render.com and sign up/login
2. Click **New +** > **Web Service**
3. Select **Connect Your Repository**
4. Find and select your `satya-setu` repository
5. Fill in the details:
   - **Name**: `satya-setu-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements-deploy.txt`
   - **Start Command**: `cd backend && gunicorn app:app`
   - **Instance Type**: Choose based on your needs (Free tier available)

#### 3. Set Environment Variables in Render
In Render dashboard > Environment:
```
DATABASE_URL=postgresql://neondb_owner:npg_hfB81OmvyFuY@ep-autumn-grass-a1q7xa4i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=793bc6a1f30ae23d72e7857dc92f4c335cfa6ad24d09fff99279e28af3bacb54
EMAIL_SENDER=pictsppu@gmail.com
EMAIL_PASSWORD=wjwt wscb yoom llck
PYTHON_VERSION=3.10.15
```

#### 4. Deploy
1. Click **Create Web Service**
2. Render will automatically build and deploy your app
3. You'll get a URL like: `https://satya-setu-dashboard.onrender.com`

---

## Option 2: Deploy Frontend to Vercel (Optional)

**Note**: Vercel works best with static sites or Next.js. Since you have HTML templates served by Flask, it's better to keep the entire app on Render. Only use Vercel if you convert to a separate frontend.

### If you still want to try Vercel:
1. Extract the `frontend/` folder as a separate project
2. Create a `vercel.json` in frontend root:
```json
{
  "buildCommand": "echo 'Frontend only - no build needed'",
  "outputDirectory": "."
}
```
3. Push to a separate GitHub repo
4. Connect to Vercel and deploy

---

## Option 3: Quick Local Testing Before Deploy

Test the PostgreSQL connection locally:

```bash
# Activate venv
.venv\Scripts\activate

# Set environment variables (Windows PowerShell)
$env:DATABASE_URL="postgresql://neondb_owner:npg_hfB81OmvyFuY@ep-autumn-grass-a1q7xa4i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# Install gunicorn
pip install gunicorn

# Test Render's startup command locally
cd backend
gunicorn app:app
```

---

## Troubleshooting

### Database Connection Error
- Check DATABASE_URL in Render environment variables
- Ensure NeonDB project is active
- Test connection: `psql YOUR_CONNECTION_STRING`

### Port Issues
- Render automatically assigns a port via `$PORT` environment variable
- Flask should listen on all interfaces: `app.run(host='0.0.0.0')`

### Module Not Found
- Ensure `requirements-deploy.txt` includes all dependencies
- Render uses `requirements-deploy.txt` due to Procfile specification

### Stuck on Build
- Check Render logs in dashboard
- Push to GitHub again to trigger rebuild
- Check for syntax errors in app.py

---

## Post-Deployment

1. **Update DNS** if using custom domain
2. **Test all endpoints**:
   - Login page: `https://your-url.onrender.com/`
   - API endpoints: `/api/upload`, `/api/dashboard`, etc.
3. **Monitor logs**: View in Render dashboard > Logs tab
4. **Setup auto-redeploy**: Enable "Auto-deploy on push" in Render settings

---

## Security Checklist

- ✅ Store secrets in environment variables (never commit them)
- ✅ Update JWT_SECRET to a unique value in production
- ✅ Use HTTPS only (Render provides SSL by default)
- ✅ Validate file uploads on backend
- ✅ Sanitize user inputs (check Flask-WTF)

---

## Next Steps

1. Create GitHub repository
2. Push code with `git push`
3. Connect Render to GitHub
4. Set environment variables
5. Deploy and test!

Questions? Check Render docs: https://render.com/docs
