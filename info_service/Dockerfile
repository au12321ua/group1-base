FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --group dev --frozen

COPY shared/ ./shared/
COPY info_service/ ./info_service/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app

RUN chmod +x /app/info_service/start.sh

WORKDIR /app/info_service
EXPOSE 8002
CMD ["bash", "/app/info_service/start.sh"]
