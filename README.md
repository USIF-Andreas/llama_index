# llama_index

LlamaIndex + OpenRouter full-stack app for complex data sources (PDFs, Google Drive, MySQL) with citations and streaming answers.

## What is inside

- FastAPI backend with LlamaIndex indexing and chat endpoints
- Vite + React frontend with streaming UI
- Docker compose for local dev

## Quick start (Docker)

1. Copy environment file and set secrets:
	- `cp .env.example .env`
2. Put your Google OAuth client secret at `/data/google/client_secret.json` (or update `GOOGLE_CLIENT_SECRET`).
3. Run the stack:
	- `docker compose up --build`
4. Open the UI at http://localhost:5173

## MySQL setup (Docker)

Docker Compose starts a MySQL service with sample data:

- Database: `llama_index`
- User: `app`
- Password: `app123`
- Root password: `RootPass123`

You can change these in `.env` and restart the stack.

## Google Drive OAuth setup

To generate a token locally (first time only):

1. Place the client secret at `/data/google/client_secret.json`.
2. Run: `python backend/scripts/gdrive_oauth.py`.
3. The token is saved at `/data/google/token.json`.

## Local dev without Docker

Backend:

1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

Frontend:

1. `cd frontend`
2. `npm install`
3. `npm run dev`

## API overview

- `POST /api/index/upload` - upload PDFs
- `POST /api/index/ingest` - ingest PDFs/Drive/MySQL
- `POST /api/chat` - single response
- `POST /api/chat/stream` - streaming response (SSE)