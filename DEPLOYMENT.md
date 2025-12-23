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

2. **Deploy to Hugging Face Spaces**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces).
   - Click **Create new Space**.
   - Choose **Docker** as the Space SDK.
   - Select **Public** or **Private** visibility.
   - Connect your GitHub repository.
   - Hugging Face will build and deploy your Dockerfile.
   - **Important**: You need to set the `GEMINI_API_KEY` environment variable in the Hugging Face Space settings ("Variables and secrets").

3. **Link Frontend to Backend**
   - Once the Space is "Running" on Hugging Face, copy its Direct URL (e.g., `https://anantwdev-forexbot.hf.space`).
   - Go to your Vercel Project Settings -> **Environment Variables**.
   - Update `VITE_API_URL`:
     - Value: `<YOUR_HF_SPACE_URL>` (No trailing slash)
   - **Crucial**: Go to deployments and click **Redeploy** on Vercel for the change to take effect.

## Frontend Configuration
The frontend uses `VITE_API_URL` to connect to the backend.
- **Local**: Defaults to `/api` (proxy).
- **Production**: MUST be set to your Hugging Face Space URL.

## Notes
- The Gemini API Key is currently hardcoded in `backend/bot/chatbot_service.py`. It is highly recommended to use Environment Variables for security.

## Telegram Notifications Setup (Vercel Relay)
This project uses a **Vercel Serverless Function** (`api/telegram.js`) to relay messages to Telegram, keeping your bot token secure on the Vercel side if desired, or acting as a proxy.

### 1. Configure Vercel Environment Variables
Go to your Vercel Project Settings -> **Environment Variables** and add:
- `TELEGRAM_BOT_TOKEN`: Your BotFather token.
- `TELEGRAM_CHAT_ID`: Your target chat ID.
- `RELAY_SECRET`: (Optional) A secret string (e.g., `my_super_secret_key`) to prevent unauthorized use.

### 2. Configure Backend Environment Variables
Where your backend runs (e.g., Hugging Face Spaces), add:
- `VERCEL_RELAY_URL`: `https://<your-vercel-app>.vercel.app/api/telegram` (e.g. `https://forex-bot-psi.vercel.app/api/telegram`)
- `RELAY_SECRET`: Must match the secret set in Step 1.

**Note:** The backend will fallback to direct Telegram API calls if `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are present in the backend environment and the relay fails or is not configured.
