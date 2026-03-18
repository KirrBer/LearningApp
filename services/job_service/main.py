"""Job service entrypoint.

Этот модуль содержит минимальную конфигурацию FastAPI-приложения.
Будет полезно добавлять сюда middleware, инициализацию зависимостей и настройки логирования.
"""

from fastapi import FastAPI
from .routes import router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Подключаем маршруты из модуля routes.py
app.include_router(router)