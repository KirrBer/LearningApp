#!/bin/bash

while ! pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t 5; do
    echo "🔄 PostgreSQL еще не готов"
    sleep 3
done

# Запускаем миграции
echo "Running migrations..."
alembic upgrade head

echo "3️⃣ Добавляю данные в БД..."
python seed_data.py


# Запускаем приложение
exec "$@"