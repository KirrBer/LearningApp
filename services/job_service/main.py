"""Job service entrypoint.

Этот модуль содержит минимальную конфигурацию FastAPI-приложения.
Будет полезно добавлять сюда middleware, инициализацию зависимостей и настройки логирования.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .routes import router
import logging
import traceback
from contextlib import asynccontextmanager
from job_service.threadpool import threadpool_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    threadpool_manager.create()

    yield

    threadpool_manager.stop()

app = FastAPI(
    title="Job Service",
    description="API сервис для поиска вакансий по резюме",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем маршруты из модуля routes.py
app.include_router(router)


# Глобальный обработчик исключений для неожиданных ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Обработчик для неожиданных исключений."""
    logger.error(f"Неожиданная ошибка: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ошибка сервера. Пожалуйста, попробуйте позже",
            "request_path": str(request.url)
        }
    )


# Обработчик для ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик для ошибок валидации входных данных."""
    logger.warning(f"Ошибка валидации для {request.method} {request.url}: {exc}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации входных данных",
            "errors": exc.errors()
        }
    )

