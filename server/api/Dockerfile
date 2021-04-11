FROM python:3.8.6-slim AS base

RUN pip install pipenv

WORKDIR /usr/app

ARG DOCKER_USER_ID

RUN groupadd picture
RUN useradd --create-home -r -o --uid ${DOCKER_USER_ID} -g picture picture

WORKDIR /usr/app

RUN chown -R picture:picture /usr/app


FROM base as prod-deps

USER root

RUN apt-get update && apt-get install make

COPY app/Pipfile ./Pipfile
COPY app/Pipfile.lock ./Pipfile.lock
RUN pipenv install --system

USER picture


FROM prod-deps as dev-deps

USER root

RUN pipenv install --system --dev

USER picture


FROM prod-deps as prod

COPY app/src ./src
COPY app/main.py ./main.py

CMD ["gunicorn", "main:app"]


FROM dev-deps as dev

COPY app/src ./src
COPY app/main.py ./main.py
COPY app/unittests ./unittests

CMD ["python", "main.py"]
