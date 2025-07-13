# Deployment Configuration

## Frontend Environment Variables

To deploy the frontend with your Render backend, you need to set the following environment variable:

### For Vercel Deployment:
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Add a new variable:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-render-backend-url.onrender.com`

### For Local Development:
Create a `.env` file in the `frontend/` directory with:
```
REACT_APP_API_URL=https://your-render-backend-url.onrender.com
```

## Backend URL Format
Replace `your-render-backend-url` with your actual Render service URL.

For example:
- `https://klarity-backend-xyz.onrender.com`
- `https://my-app-backend.onrender.com`

## Testing
After setting the environment variable:
1. Redeploy your frontend on Vercel
2. Test the connection by submitting a YouTube URL
3. Check browser console for any CORS or network errors

## Troubleshooting
- Make sure your Render backend is running and accessible
- Verify the URL format (include https://)
- Check that CORS is properly configured in your backend
- Ensure environment variable is set in your deployment platform 