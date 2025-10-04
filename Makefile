up:
	docker compose -f docker-compose.dev.yml up --build -d

down:
	docker compose -f docker-compose.dev.yml down -v

logs:
	docker compose -f docker-compose.dev.yml logs -f web

makemigrations:
	docker compose -f docker-compose.dev.yml exec web uv run python manage.py makemigrations

migrate:
	docker compose -f docker-compose.dev.yml exec web uv run python manage.py migrate

shell:
	docker compose -f docker-compose.dev.yml exec web uv run python manage.py shell

prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down -v
