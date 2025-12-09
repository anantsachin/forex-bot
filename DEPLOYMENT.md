# Deployment Guide

## Status
- **Frontend**: ✅ Deployed to Vercel
- **Backend**: ⚠️ Not deployed (exceeds Vercel's 250MB limit due to ML libraries)

## Next Steps for Backend Deployment

The backend requires a platform that supports larger container images, such as **Render** (recommended), Railway, or Fly.io.

I have already:
1. Created a `backend/Dockerfile` for containerization.
2. Created a `render.yaml` Blueprint for easy setup on Render.
3. Initialized a Git repository and cleaned up `.gitignore`.

### Instructions

1. **Push to GitHub**
   Create a new repository on GitHub and push your code:
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** -> **Blueprint**.
   - Connect your GitHub repository.
   - Render will detect `render.yaml` and set up the services.
   - **Important**: You need to set the `GEMINI_API_KEY` environment variable in the Render dashboard if you remove it from the code.

3. **Link Frontend to Backend**
   - Once the Backend is valid on Render, copy its URL (e.g., `https://forex-bot-backend.onrender.com`).
   - Go to your Vercel Project Settings -> **Environment Variables**.
   - Add a new variable:
     - Key: `VITE_API_URL`
     - Value: `<YOUR_RENDER_BACKEND_URL>` (Do not include a trailing slash, e.g., `https://my-backend.onrender.com`)
   - Redeploy the Frontend on Vercel.

## Frontend Configuration (404 Fix)
The frontend has been updated to use the `VITE_API_URL` environment variable.
- **Local Development**: If `VITE_API_URL` is not set, it defaults to `/api`, which works with the local Vite proxy.
- **Production**: You **MUST** set `VITE_API_URL` in Vercel to point to your deployed backend. Without this, API calls will fail with 404.

## Notes
- The Gemini API Key is currently hardcoded in `backend/bot/chatbot_service.py`. It is highly recommended to use Environment Variables for security.
