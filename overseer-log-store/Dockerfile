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

EXPOSE 5421
ENTRYPOINT pipenv run alembic upgrade head && pipenv run uvicorn overseer.main:overseer --port 5421 --host 0.0.0.0
