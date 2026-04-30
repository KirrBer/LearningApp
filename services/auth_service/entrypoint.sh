#!/bin/bash


while ! pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t 5; do
    echo "🔄 PostgreSQL еще не готов"
    sleep 3
done

echo "PostgreSQL started"

echo "Running migrations..."
alembic upgrade head

exec "$@"