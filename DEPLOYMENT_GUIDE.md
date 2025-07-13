# Klarity App Deployment Guide

## Overview
This guide walks you through deploying your Klarity app using Render (backend) and Vercel (frontend) - both free tiers.

## Prerequisites
- Git installed
- GitHub account
- Render account ([render.com](https://render.com))
- Vercel account ([vercel.com](https://vercel.com))
- Your Google Gemini API key

## Step 1: Push to GitHub

### Fix PowerShell Commands
Since you're using PowerShell, use these commands instead of `&&`:

```powershell
# Navigate to your project root
cd C:\Users\bhuva\Klarity

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit - Klarity movie recommendation app"

# Add your GitHub repository (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/klarity-app.git

# Push to GitHub
git push -u origin main
```

### If you get push errors:
```powershell
# If branch doesn't exist, create it
git branch -M main

# Force push if needed (only for initial setup)
git push -u origin main --force
```

## Step 2: Deploy Backend to Render

### A. Create Web Service
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your `klarity-app` repository

### B. Configure Build Settings
- **Name**: `klarity-backend`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --host=0.0.0.0 --port=$PORT`

### C. Set Environment Variables
In the Render dashboard, add these environment variables:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_ENV=production
FRONTEND_URL=https://your-app-name.vercel.app
```

### D. Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Copy your backend URL (e.g., `https://klarity-backend.onrender.com`)

## Step 3: Deploy Frontend to Vercel

### A. Create Project
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Select your `klarity-app` repository

### B. Configure Build Settings
- **Framework Preset**: Create React App
- **Root Directory**: `frontend/klarity-frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `build`

### C. Set Environment Variables
In the Vercel dashboard, add this environment variable:
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```
Replace `your-backend-url` with your actual Render backend URL.

### D. Deploy
- Click "Deploy"
- Wait for deployment (2-5 minutes)
- Your app will be live at `https://your-app-name.vercel.app`

## Step 4: Update Backend CORS

After both deployments:

1. Go back to your Render dashboard
2. Update the `FRONTEND_URL` environment variable with your actual Vercel URL
3. Your backend will automatically redeploy

## Step 5: Test Your Deployment

1. Visit your Vercel URL
2. Test the health check: `https://your-backend-url.onrender.com/health`
3. Try processing a YouTube video
4. Check that all features work

## Common Issues & Solutions

### Backend Issues
- **"Application failed to respond"**: Check logs in Render dashboard
- **API key errors**: Verify `GEMINI_API_KEY` is set correctly
- **CORS errors**: Ensure `FRONTEND_URL` matches your Vercel domain

### Frontend Issues
- **API connection errors**: Verify `REACT_APP_API_URL` is set correctly
- **Build failures**: Check if all dependencies are in `package.json`
- **Routing issues**: The `vercel.json` should handle this

### Database Issues
- **SQLite not persisting**: Render's free tier has ephemeral storage
- **Solution**: Consider upgrading to PostgreSQL (still free on Render)

## Environment Variables Summary

### Backend (Render)
```
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=production
FRONTEND_URL=https://your-app-name.vercel.app
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend-name.onrender.com
```

## Important Notes

1. **Free Tier Limitations**:
   - Render: Backend sleeps after 15 minutes of inactivity
   - Vercel: 100GB bandwidth, 300 build minutes per month
   - First request after sleep may take 30+ seconds

2. **Database**: SQLite data will be lost on Render restarts. Consider PostgreSQL for production.

3. **Custom Domain**: Both platforms support custom domains on free tiers.

4. **SSL**: Both platforms provide free SSL certificates.

## Troubleshooting Commands

### Check if backend is running:
```bash
curl https://your-backend-url.onrender.com/health
```

### Check Render logs:
- Go to Render dashboard → Your service → Logs tab

### Check Vercel logs:
- Go to Vercel dashboard → Your project → Functions tab

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Monitor usage and performance
3. Consider setting up monitoring/alerts
4. Plan for database migration if needed

Your Klarity app should now be live and accessible worldwide! 🎉 