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
from skill_analyzer.threadpool import threadpool_manager
from skill_analyzer.exceptions import ModelLoadingError, ThreadPoolError

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


    # Создаем threadpool
    try:
        threadpool_manager.create()
        logger.info("✅ Threadpool created successfully")
    except ThreadPoolError as e:
        logger.error(f"❌ Failed to create threadpool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during threadpool creation: {str(e)}")
        raise

    yield

    # Очищаем ресурсы при остановке приложения.
    try:
        model_manager.unload_models()
        logger.info("✅ Models unloaded successfully")
    except Exception as e:
        logger.error(f"❌ Error unloading models: {str(e)}")

    try:
        threadpool_manager.stop()
        logger.info("✅ Threadpool stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping threadpool: {str(e)}")
 
app = FastAPI(lifespan=lifespan)

# Роуты находятся в skill_analyzer/routes.py
app.include_router(router)