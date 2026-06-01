#!/bin/bash
set -e

echo "==> Starting Info Service..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8002
