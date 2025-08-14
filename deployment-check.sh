#!/bin/bash

echo "🚀 Vercel Deployment Readiness Check"
echo "===================================="

# Check if required files exist
echo "📋 Checking required files..."

files=("app.py" "index.py" "database.py" "vercel.json" "requirements.txt" "runtime.txt" ".gitignore")
templates=("templates/auth.html" "templates/dashboard.html")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING!"
    fi
done

for template in "${templates[@]}"; do
    if [ -f "$template" ]; then
        echo "✅ $template"
    else
        echo "❌ $template - MISSING!"
    fi
done

echo ""
echo "🔧 Configuration files:"
if [ -f "vercel.json" ]; then
    echo "✅ vercel.json configured for Python"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt with all dependencies"
fi

if [ -f "runtime.txt" ]; then
    echo "✅ runtime.txt specifies Python version"
fi

echo ""
echo "📝 Environment Variables needed in Vercel:"
echo "- SECRET_KEY"
echo "- MONGODB_URI" 
echo "- RAZORPAY_KEY_ID"
echo "- RAZORPAY_KEY_SECRET"
echo "- CUSTOM_API_KEY"
echo "- FREE_TRIAL_LIMIT"

echo ""
echo "🎯 Ready for deployment!"
echo "Next steps:"
echo "1. git init && git add . && git commit -m 'Initial commit'"
echo "2. Push to GitHub repository"
echo "3. Deploy on Vercel by importing the GitHub repo"
echo "4. Add environment variables in Vercel dashboard"
echo ""
echo "Your app will be live at: https://your-project-name.vercel.app"
