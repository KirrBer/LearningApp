"""Skill Analyzer service entrypoint.

При запуске сервиса:
- загружаются ML-модели (spaCy + T5)
- устанавливается Kafka-соединение (для публикации результатов)

При остановке модели выгружаются.
"""

from fastapi import FastAPI
from skill_analyzer.routes import router
from skill_analyzer.model_manager import model_manager
from skill_analyzer.kafka import kafka_manager
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загружаем модели один раз при старте, чтобы первый запрос был быстрым.
    model_manager.load_models()

    # Запускаем Kafka producer/consumer.
    await kafka_manager.start()

    yield

    # Очищаем ресурсы при остановке приложения.
    model_manager.unload_models()
    await kafka_manager.stop()
 
app = FastAPI(lifespan=lifespan)

# Роуты находятся в skill_analyzer/routes.py
app.include_router(router)