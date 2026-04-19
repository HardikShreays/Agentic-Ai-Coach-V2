# Deployment Guide

## Architecture

- Frontend: Vercel (`frontend/`)
- Backend: Render (`backend/`)

## Frontend (Vercel)

1. Import the repo in Vercel.
2. Set Root Directory to `frontend`.
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variable:
   - `VITE_API_URL=https://<your-render-backend-domain>`

`frontend/vercel.json` is configured for SPA route rewrites.

## Backend (Render)

Use `render.yaml` or configure manually:

- Root Directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Set env vars from `backend/.env.example` and ensure:

- `COOKIE_SECURE=true`
- `COOKIE_SAMESITE=none`
- `FRONTEND_ORIGIN=https://<your-vercel-domain>`
- `MONGO_URL` and `JWT_SECRET` are set
- `INGEST_KB_ON_STARTUP=true` (optional, if you want seed KB auto-ingest)

For multiple frontend domains, use comma-separated origins in `FRONTEND_ORIGIN`.
