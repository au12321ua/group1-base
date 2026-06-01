FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --group dev --frozen

COPY shared/ ./shared/
COPY auth_service/ ./auth_service/
COPY info_service/ ./info_service/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "-m", "scripts.seed_data"]
