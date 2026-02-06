# Property Hub Development Commands

# Start development services with Docker
up:
    docker compose -f docker-compose.dev.yml up -d

# Stop development services
down:
    docker compose -f docker-compose.dev.yml down -v

# Start Django development server with CSS build
runserver port="8000":
    npm run build-css &
    uv run python manage.py runserver_plus localhost:{{port}}

# Create new Django migrations
makemigrations:
    uv run python manage.py makemigrations

# Apply Django migrations
migrate:
    uv run python manage.py migrate

# Start production services with Docker
prod-up:
    docker compose -f docker-compose.prod.yml up --build -d

# Stop production services
prod-down:
    docker compose -f docker-compose.prod.yml down -v

# Install Python dependencies
build:
    uv sync

# Type check with ty (manual run)
type-check:
    uv run ty check .

# Show available commands
help:
    @just --list
