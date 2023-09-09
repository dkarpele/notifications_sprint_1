FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt \
    && apt-get update && apt-get install -y netcat

COPY . ./src