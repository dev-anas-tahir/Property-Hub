# Stage 1: Build CSS and collect static
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /bin/uv

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock package.json package-lock.json ./
RUN uv sync --frozen --no-dev && npm ci

COPY . .
RUN npm run build-css-prod

ARG SECRET_KEY=dummy-build-only-key
ARG ALLOWED_HOSTS=localhost
ARG DEBUG=False
ARG DATABASE_URL
ENV SECRET_KEY=${SECRET_KEY} ALLOWED_HOSTS=${ALLOWED_HOSTS} DEBUG=${DEBUG} DATABASE_URL=${DATABASE_URL}
ENV DJANGO_SETTINGS_MODULE=config.settings.production
RUN uv run python manage.py collectstatic --noinput

# Stage 2: Lean runtime image
FROM python:3.13-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/staticfiles /app/staticfiles
COPY --chown=appuser:appuser . /app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["uv", "run", "daphne", \
    "-b", "0.0.0.0", \
    "-p", "8000", \
    "--access-log", "-", \
    "-v", "1", \
    "config.asgi:application"]
