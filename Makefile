.PHONY: build migrate runserver rungunicorn test shell

build:
	pip install uv
	uv sync

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate
	uv run python manage.py collectstatic --noinput

runserver:
	uv run python manage.py runserver

rungunicorn:
	uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=1 --timeout=120

test:
	uv run pytest

shell:
	uv run python manage.py shell
