#!/bin/bash
set -e

echo "=== CareerMatch Backend Starting ==="
echo "PORT: ${PORT:-8000}"
echo "DATABASE_URL prefix: ${DATABASE_URL:0:20}..."

echo "Running Alembic migrations..."
python -m alembic upgrade head || echo "Alembic warning (may already be applied)"

echo "Starting uvicorn..."
exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
