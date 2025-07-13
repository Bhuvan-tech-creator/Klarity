# Deployment Configuration

## Backend Environment Variables (For Render)

Set these environment variables in your Render dashboard:

```
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=https://your-frontend-domain.vercel.app
FLASK_ENV=production
PORT=5000
```

## Build Commands for Render

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --host=0.0.0.0 --port=$PORT`

## Frontend Environment Variables (For Vercel)

Set these in your Vercel dashboard:

```
REACT_APP_API_URL=https://your-backend-domain.render.com
``` 