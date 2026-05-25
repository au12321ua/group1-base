FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --group dev --frozen

COPY shared/ ./shared/
COPY auth_service/ ./auth_service/

ENV PYTHONPATH=/app

RUN chmod +x /app/auth_service/start.sh

WORKDIR /app/auth_service
EXPOSE 8001
CMD ["bash", "/app/auth_service/start.sh"]
