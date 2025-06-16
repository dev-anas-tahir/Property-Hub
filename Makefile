.PHONY: build migrate runserver rungunicorn test shell

build:
	pip install pipenv
	pipenv install --dev

migrate:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate
	pipenv run python manage.py collectstatic --noinput

runserver:
	pipenv run python manage.py runserver

rungunicorn:
	pipenv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=1 --timeout=120

test:
	pipenv run pytest

shell:
	pipenv run python manage.py shell
