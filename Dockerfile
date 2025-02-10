FROM python:3.10-slim

WORKDIR /app

COPY /pyproject.toml /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY . .

LABEL project='referral_system_service' version=1.0