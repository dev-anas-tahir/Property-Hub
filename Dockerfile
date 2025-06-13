# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIPENV_VENV_IN_PROJECT=true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip pipenv

COPY Pipfile Pipfile.lock /app/
RUN pipenv install --ignore-pipfile

COPY . /app/

RUN pipenv run python manage.py collectstatic --noinput

# CMD ["pipenv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--timeout=120"]
CMD ["sh", "-c", "pipenv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=3 --timeout=120 --access-logfile=- --error-logfile=-"]
