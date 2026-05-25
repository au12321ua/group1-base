#!/bin/bash
set -e

echo "==> Creating data directory..."
mkdir -p /app/info_service/data

echo "==> Running Info DB migrations..."
uv run alembic -c migrations/info/alembic.ini upgrade head

echo "==> Running Audit DB migrations..."
uv run alembic -c migrations/audit/alembic.ini upgrade head

echo "==> Starting Info Service..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8002
