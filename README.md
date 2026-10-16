# CyberQuest AI

CyberQuest AI is a game-based cybersecurity learning platform built with React + Vite on the frontend and FastAPI on the backend. It includes secure authentication, challenge tracking, AI-style simulations, adaptive scoring, XP and badges, and demo data for local development.

## Features

- Learner dashboard with XP, badges, and skill progress
- Learning path and challenge library
- AI simulation arena with mock AI fallback mode
- Adaptive decision evaluation and scoring
- Admin and trainer dashboards
- SQLite for local development, PostgreSQL ready for production
- Test coverage for authentication and core API flows

## Local setup

1. Open a terminal in the project root.
2. Create and activate a Python virtual environment.
3. Install backend dependencies:

   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

4. Start the backend:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. In a second terminal, install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

6. Start the frontend:

   ```bash
   npm run dev
   ```

7. Open http://localhost:5173 in the browser.

## Demo credentials

Use these development credentials when running locally:

- Learner: `learner@demo.local` / `demo123`
- Trainer: `trainer@demo.local` / `demo123`
- Admin: `admin@demo.local` / `demo123`

## Environment variables

Copy the `.env.example` file into `.env` and adjust values as needed.

## Backend tests

```bash
cd backend
pytest
```

## Frontend build check

```bash
cd frontend
npm run build
```

## Project structure

- `backend/app` — FastAPI app, models, API routes, and services
- `frontend/src` — React components and app logic
- `database` — database persistence and migration-ready folder
- `README.md` — setup documentation
- `docker-compose.yml` — local container orchestration template
