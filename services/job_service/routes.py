"""Маршруты API для Job Service.

Здесь зарегистрированы endpoint-ы, которые отвечают за работу с вакансиями.
"""

from fastapi import APIRouter, Body, File, UploadFile, HTTPException, status
from job_service.utils import recommendations_sort, extract_text_from_pdf
from job_service.schemas import ResumeRequest, VacancyResponse, ShortVacancyResponse
from job_service.db_methods import get_vacancy_by_id
from typing import List
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/recommendations_from_text", summary="Получить список рекомендаций для резюме из текста", response_model=List[ShortVacancyResponse])
async def get_recommendations(data: ResumeRequest = Body(...)) -> List[ShortVacancyResponse]:
    """
    Получает рекомендации вакансий на основе текста резюме.
    
    Args:
        data: Объект с текстом резюме
        
    Returns:
        Список вакансий, отсортированных по релевантности
        
    Raises:
        HTTPException: При ошибке обработки резюме или БД
    """
    try:
        # Валидация входных данных
        if not data.resume or not data.resume.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Резюме не может быть пустым"
            )
        
        if len(data.resume) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Резюме слишком длинное (максимум 50000 символов)"
            )
        
        response = await recommendations_sort(data.resume)
        
        if not response:
            logger.warning("Не найдены вакансии для резюме")
            return []
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Ошибка валидации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка обработки резюме: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке резюме: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке резюме. Пожалуйста, попробуйте позже"
        )


@router.post("/recommendations_from_pdf", summary="Получить список рекомендаций для резюме из PDF", response_model=List[ShortVacancyResponse])
async def get_recommendations_pdf(file: UploadFile = File(...)) -> List[ShortVacancyResponse]:
    """
    Получает рекомендации вакансий на основе загруженного PDF файла.
    
    Args:
        file: Загруженный PDF файл
        
    Returns:
        Список вакансий, отсортированных по релевантности
        
    Raises:
        HTTPException: При ошибке загрузки, парсинга PDF или обработки БД
    """
    def long_to_short_vacancy_response(vacancy):
        return ShortVacancyResponse(
            id=vacancy.id,
            name=vacancy.name,
            employer=vacancy.employer,
            salary=vacancy.salary,
            area=vacancy.area
        )
    try:
        # Валидация типа файла
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Допускается только PDF файлы"
            )
        
        # Проверка размера файла (максимум 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла не должен превышать 10MB"
            )
        
        # Извлечение текста из PDF
        data = await extract_text_from_pdf(file)
        
        if not data or not data.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось извлечь текст из PDF файла"
            )
        
        # Получение рекомендаций
        sorted_vacancies = await recommendations_sort(data)
        response = [long_to_short_vacancy_response(v) for v in sorted_vacancies]
        if not response:
            logger.warning("Не найдены вакансии для загруженного PDF")
            return []
        
        return response


        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Ошибка при парсинге PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ошибка при чтении PDF файла. Убедитесь, что файл не поврежден"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке PDF файла. Пожалуйста, попробуйте позже"
        )


@router.get("/vacancies/{id}", summary="Получить вакансию по id", response_model=VacancyResponse)
async def get_vacancy(id) -> VacancyResponse:
    vacancy = await get_vacancy_by_id(int(id))
    if vacancy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вакансия не найдена"
        )
    return vacancy

@router.get("/health", summary="Проверка статуса сервиса")
def health():
    """
    Проверка доступности сервиса.
    
    Returns:
        Статус сервиса
    """
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Ошибка в health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен"
        )