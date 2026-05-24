#!/bin/bash
set -e

echo "==> Creating data directory..."
mkdir -p /app/auth_service/data

echo "==> Running Auth Service database migrations..."
uv run alembic -c migrations/alembic.ini upgrade head

echo "==> Starting Auth Service..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8001
