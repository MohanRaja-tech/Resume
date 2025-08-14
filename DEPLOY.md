# Vercel Deployment Guide

## Quick Deploy Steps

### 1. Prepare Repository
```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Resume Summary Generator"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/resume-summary-generator.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy on Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your GitHub repository

2. **Environment Variables**:
   In Vercel dashboard, add these environment variables:
   ```
   SECRET_KEY=your-super-secret-key-change-this-in-production
   MONGODB_URI=mongodb+srv://mohantwo3:Mohan%402006@cluster0.gs12h0u.mongodb.net/resume_generator?retryWrites=true&w=majority
   RAZORPAY_KEY_ID=rzp_live_R5AQxNLHPa1UB2
   RAZORPAY_KEY_SECRET=zqWbA2CGQCFCrLvPsuclm1Ii
   CUSTOM_API_KEY=test_api_key_placeholder
   FREE_TRIAL_LIMIT=3
   ```

3. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be live at `https://your-project-name.vercel.app`

### 3. Post-Deployment

1. **Test the application**:
   - Visit your Vercel URL
   - Test user registration/login
   - Test resume generation
   - Test payment flow

2. **Monitor**:
   - Check Vercel function logs
   - Monitor MongoDB Atlas connections
   - Check Razorpay dashboard for payments

## Files Configured for Vercel

✅ `vercel.json` - Vercel configuration
✅ `index.py` - Entry point for Vercel
✅ `app.py` - Main Flask application (Vercel compatible)
✅ `requirements.txt` - Dependencies
✅ `runtime.txt` - Python version
✅ `.gitignore` - Git ignore rules

## Ready to Deploy! 🚀

Your project is now fully configured for Vercel deployment.
