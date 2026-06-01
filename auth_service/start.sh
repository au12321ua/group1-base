#!/bin/bash
set -e

echo "==> Starting Auth Service..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8001
