# Render Deployment Guide for Resume Summary App

## 🚀 Deploy on Render

### Step 1: Create Web Service
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Select "New" → "Web Service"
4. Choose your repository: `MohanRaja-tech/Resume`

### Step 2: Configuration
- **Name**: `resume-summary-app`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn index:application`
- **Instance Type**: Free (or upgrade as needed)

### Step 3: Environment Variables
Add these environment variables in Render dashboard:

```
SECRET_KEY=sk_5f8a2b9c4e6d1a3b7f9e2c8d4a6b9e3f7c1a5b8d2e6f9c3a7b4e8d1f5a9c2b6e8d3f
FLASK_ENV=production
MONGODB_URI=mongodb+srv://mohantwo3:Mohan%402006@cluster0.gs12h0u.mongodb.net/resume_generator?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE
RAZORPAY_KEY_ID=rzp_live_R5AQxNLHPa1UB2
RAZORPAY_KEY_SECRET=zqWbA2CGQCFCrLvPsuclm1Ii
CUSTOM_API_KEY=no_auth_required
FREE_TRIAL_LIMIT=3
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will automatically deploy your app
3. Your app will be available at: `https://your-app-name.onrender.com`

## 📋 Files Structure (Ready for Render)
- `index.py` - WSGI entry point
- `app.py` - Main Flask application
- `database.py` - Database operations
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `templates/` - HTML templates

## ✅ Benefits of Render vs Vercel
- Better for Python Flask apps
- Easier environment variable management
- Built-in logging and monitoring
- Free tier with persistent storage
- No serverless function limitations

Your app is now ready for Render deployment! 🎉
