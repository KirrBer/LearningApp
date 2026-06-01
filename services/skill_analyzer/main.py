"""Skill Analyzer service entrypoint.

При запуске сервиса:
- загружаются ML-модели (spaCy + T5)
- устанавливается Kafka-соединение (для публикации результатов)

При остановке модели выгружаются.
"""

from fastapi import FastAPI
from skill_analyzer.routes import router
from skill_analyzer.model_manager import model_manager
from contextlib import asynccontextmanager
import logging
from skill_analyzer.threadpool import process_pool_manager
from skill_analyzer.exceptions import ModelLoadingError, ProcessPoolError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загружаем модели один раз при старте, чтобы первый запрос был быстрым.
    try:
        model_manager.load_models()
        logger.info("✅ Models loaded successfully")
    except ModelLoadingError as e:
        logger.error(f"❌ Failed to load models: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during model loading: {str(e)}")
        raise

    # Запускаем Kafka producer/consumer.


    # Создаем пул процессов для CPU-bound ML inference
    try:
        process_pool_manager.create()
        logger.info("✅ Process pool created successfully")
    except ProcessPoolError as e:
        logger.error(f"❌ Failed to create process pool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during process pool creation: {str(e)}")
        raise

    yield

    # Очищаем ресурсы при остановке приложения.
    try:
        model_manager.unload_models()
        logger.info("✅ Models unloaded successfully")
    except Exception as e:
        logger.error(f"❌ Error unloading models: {str(e)}")

    try:
        process_pool_manager.stop()
        logger.info("✅ Process pool stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping process pool: {str(e)}")
 
app = FastAPI(lifespan=lifespan)

# Роуты находятся в skill_analyzer/routes.py
app.include_router(router)