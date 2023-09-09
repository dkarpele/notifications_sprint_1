#!/bin/sh

echo "Waiting for postgres on $DB_HOST:$DB_PORT ..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Waiting for rabbitmq on $RABBIT_HOST:$RABBIT_PORT ..."

while ! nc -z "$RABBIT_HOST" "$RABBIT_PORT"; do
  sleep 0.1
done

echo "rabbitmq started"

pwd
cd src && alembic upgrade head
cd ..
pwd
gunicorn -k uvicorn.workers.UvicornWorker --chdir src main:app --bind 0.0.0.0:8000 &
python src/consume.py