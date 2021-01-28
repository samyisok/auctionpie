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

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

#Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY . /code

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start