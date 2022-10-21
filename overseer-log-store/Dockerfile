FROM python:3.8

WORKDIR /var/app

RUN pip install pipenv

RUN mkdir .venv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

COPY overseer ./overseer
COPY alembic ./alembic
COPY alembic.ini .

ENV PORT 5421
ENV HOST 127.0.0.1

ENTRYPOINT pipenv run alembic upgrade head && pipenv run uvicorn overseer.main:overseer --port $PORT --host $HOST
