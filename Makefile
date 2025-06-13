.PHONY: build migrate run

build:
	pip install pipenv
	pipenv install --dev

migrate:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate
	pipenv run python manage.py collectstatic --noinput

run:
	pipenv run python manage.py runserver

test:
	pipenv run pytest

shell:
	pipenv run python manage.py shell