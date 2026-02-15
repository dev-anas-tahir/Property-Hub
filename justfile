# Property Hub Development Commands

# Start development services with Docker
up:
    docker compose -f docker-compose.yml up -d

# Stop development services
down:
    docker compose -f docker-compose.yml down -v

# Start Django development server with CSS build
runserver port="8000":
    npm run build-css &
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
