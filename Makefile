up:
	docker compose -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.dev.yml down -v

runserver:
	uv run python manage.py runserver

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down -v
