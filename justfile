# Property Hub Development Commands

# Start development services with Docker
up:
    docker compose -f docker-compose.yml up -d

# Stop development services
down:
    docker compose -f docker-compose.yml down -v

# Start Django development server with CSS & JS build
runserver port="8000":
    #!/usr/bin/env bash
    set -euo pipefail

    css_pid=""

    cleanup() {
        if [[ -n "$css_pid" ]]; then
            kill "$css_pid" 2>/dev/null || true
            wait "$css_pid" 2>/dev/null || true
        fi
    }

    trap cleanup EXIT INT TERM

    npm run build-js
    npm run build-css &
    css_pid=$!

    uv run python manage.py runserver {{port}}

# Create new Django migrations
makemigrations:
    uv run python manage.py makemigrations

# Apply Django migrations
migrate:
    uv run python manage.py migrate

# Install Python dependencies
build:
    uv sync
    npm install

# Type check with ty (manual run)
type-check:
    uv run ty check .

# Show available commands
help:
    @just --list
