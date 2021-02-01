FROM python:3.8.5-slim-buster

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.4


RUN pip install "poetry==$POETRY_VERSION"

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

#Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY . /code

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

RUN groupadd -g 999 celery && \
  useradd -r -u 999 -g celery celery

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat