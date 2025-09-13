# 🚀 Portora Deployment Guide

## Backend Environment Variables (Render)

When deploying to Render, you'll need to set these environment variables in the Render dashboard:

### Required API Keys:
1. **APCA_API_KEY_ID** - Your Alpaca API Key ID
2. **APCA_API_SECRET_KEY** - Your Alpaca API Secret Key  
3. **TWELVE_DATA_API_KEY** - Your Twelve Data API Key
4. **OPENAI_API_KEY** - Your OpenAI API Key

### Auto-Configured:
- **APCA_API_BASE_URL** - Set to "https://api.alpaca.markets"
- **SECRET_KEY** - Auto-generated secure secret for JWT
- **PORT** - Set to 10000 (Render requirement)

## How to Get API Keys:

### 1. Alpaca API (Free)
- Go to [alpaca.markets](https://alpaca.markets)
- Sign up for a free account
- Go to Paper Trading → API Keys
- Copy your Key ID and Secret Key

### 2. Twelve Data API (Free)
- Go to [twelvedata.com](https://twelvedata.com)
- Sign up for a free account
- Go to API Keys section
- Copy your API key

### 3. OpenAI API (Paid)
- Go to [platform.openai.com](https://platform.openai.com)
- Sign up and add billing
- Go to API Keys section
- Create a new API key

## Frontend Environment Variables (Vercel)

Set this in Vercel dashboard:
- **NEXT_PUBLIC_API_URL** - Your Render backend URL (e.g., https://portora-backend.onrender.com)

## Deployment Steps:

### 1. Backend (Render)
1. Go to render.com → New Web Service
2. Connect GitHub: kishore7cm/Portora
3. Configure:
   - Name: portora-backend
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`
4. Set Environment Variables (see above)
5. Deploy

### 2. Frontend (Vercel)
1. Go to vercel.com → New Project
2. Import from GitHub: kishore7cm/Portora
3. Set Root Directory: `frontend`
4. Set Environment Variable: `NEXT_PUBLIC_API_URL` = your backend URL
5. Deploy

## Testing Deployment:

- Backend Health: `https://your-backend-url.onrender.com/health`
- Frontend: `https://your-frontend-url.vercel.app`
- Login: demo@portora.com / 123456
