# Personal Protocol Manager

Monorepo with backend API (FastAPI), Telegram bot (Aiogram), and Mini App frontend (Vite + React).

## Structure
- `backend/` FastAPI app + services + storage
- `bot/` Telegram bot handlers
- `frontend/` Mini App UI

## Local setup (rough)
1) Backend
- Create a venv and install `backend/requirements.txt`
- Set `DATABASE_URL` and `BOT_TOKEN`
- Run: `uvicorn app.main:app --reload --app-dir backend`

2) Migrations
- Run: `alembic -c backend/alembic.ini upgrade head`

3) Bot
- Reuse the same venv + env vars
- Run: `python -m bot.main`

4) Frontend
- `npm install`
- `npm run dev`

## Tests
- Install `backend/requirements-dev.txt`
- Run: `pytest backend/tests`

## Notes
- API currently trusts `user_id` without Telegram initData validation.
- Statuses are stored per protocol+item and reset when bot starts execution.
- Frontend uses Telegram WebApp init when available; otherwise falls back to user_id=123.
