# StarLab Currency Service

Async FastAPI + Celery microservice that fetches FX rates from the Russian Central Bank, lets you override them manually, converts between currencies via cached snapshots, exports CSV, and tracks endpoint latency percentiles.

## Quick start (Docker Compose)
1. Copy environment template and adjust credentials if needed:
   ```bash
   cp .env.example .env
   ```
2. Build and start everything (app, Celery worker/beat, Postgres, Redis):
   ```bash
   docker compose up --build
   ```
3. Apply migrations (from the running compose services):
   ```bash
   docker compose run --rm app alembic upgrade head
   ```

After startup:
- API docs: http://localhost:8000/docs
- Manual cron fetch runs via Celery beat (configurable by `CBR_FETCH_CRON` in `.env`).
- Run tests with coverage:
  ```bash
  pip install -r requirements.txt
  pytest --cov=app --cov=tests --cov-report=term-missing -v
  ```
