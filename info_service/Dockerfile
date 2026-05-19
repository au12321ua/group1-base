FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --group dev --frozen

COPY shared/ ./shared/
COPY info_service/ ./info_service/

ENV PYTHONPATH=/app

WORKDIR /app/info_service
EXPOSE 8002
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
