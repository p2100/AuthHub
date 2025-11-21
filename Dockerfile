# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source
COPY frontend ./

# Build frontend
RUN pnpm build

# Stage 2: Backend & Final Image
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create virtual environment
RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install system dependencies if needed (e.g. for postgres)
# python:slim usually has basic libs, but sometimes libpq-dev is needed for building psycopg2
# but we use psycopg2-binary, so it should be fine.
# If using standard psycopg2, we'd need build-essential and libpq-dev.

# Copy backend dependency configuration
COPY backend/pyproject.toml .

# Generate requirements and install dependencies
# This separates dependency installation from source code changes
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install -r requirements.txt

# Copy backend source code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .
COPY backend/scripts ./scripts

# Copy built frontend assets to backend static directory
COPY --from=frontend-builder /app/frontend/dist ./app/static

# Create keys directory
RUN mkdir -p keys

# Copy entrypoint script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Cloud Run defaults to 8080
ENV PORT=8080
ENV HOST=0.0.0.0

# Environment variables that should be overridden at runtime
ENV DATABASE_URL=""
ENV REDIS_URL=""

CMD ["./docker-entrypoint.sh"]
