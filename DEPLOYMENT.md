# Deployment Guide

## Environment Variables Required

### Render.com (Backend)
1. Go to your Render dashboard
2. Select your backend service
3. Navigate to **Environment** tab
4. Add the following environment variable:
   - **Key**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key (starts with `sk-or-v1-...`)

### Vercel (Frontend)
The frontend doesn't need the API key since it calls the backend.

## Verifying Deployment

### Check Render Backend
1. Go to Render dashboard → Your service → Logs
2. Look for: `Starting Aetheria Backend on http://0.0.0.0:5001`
3. Test the endpoint: `https://your-backend.onrender.com/api/ping`

### Check Vercel Frontend
1. Go to Vercel dashboard → Your project → Deployments
2. Ensure the latest deployment is successful
3. Visit your live URL

## Testing AI Analysis
Once deployed, test by:
1. Opening your app
2. Uploading an architectural render
3. Enabling "AI Critique" toggle
4. Clicking "Analyze Render"

If you see "No API key provided", the environment variable is not set correctly on Render.

## Local Development
For local development, ensure `.env` file contains:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```
