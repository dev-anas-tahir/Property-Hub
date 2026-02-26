# Property Hub Development Commands

# Start development services with Docker
up:
    docker compose -f docker-compose.yml up -d

# Stop development services
down:
    docker compose -f docker-compose.yml down -v

# Start Django development server with CSS & JS build
runserver port="8000":
    trap 'kill 0' SIGINT SIGTERM
    npm run build-css &
    npm run build-js &
    uv run python manage.py runserver {{port}} &
    wait

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
