#!/bin/bash

# Запускаем миграции
echo "Running migrations..."
alembic upgrade head

# Запускаем приложение
exec "$@"