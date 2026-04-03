"""API-маршруты Skill Analyzer.

Сервис принимает текст или PDF и возвращает найденные навыки + рекомендованные курсы.
Результаты также публикуются в Kafka-топик `extraction_results`.
"""

from fastapi import APIRouter, Body, File, UploadFile, HTTPException, status
from skill_analyzer.utils import extract_skills_from_text, extract_text_from_pdf, find_courses
from skill_analyzer.schemas import TextRequest, SkillResponse
from typing import List
from skill_analyzer.threadpool import threadpool_manager
from skill_analyzer.exceptions import (
    PDFExtractionError, 
    ModelInferenceError, 
    DatabaseError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/extract_skills_from_text", summary="Получить список навыков из полученного текста")
async def get_skills(data: TextRequest = Body(...)) -> List[SkillResponse]:
    """Возвращает список навыков + курсов для переданного текста."""
    
    try:
        if not data.text or len(data.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        # Нормализация и извлечение навыков выполняется в отдельном потоке,
        # чтобы не блокировать основной event loop.
        try:
            skills = await threadpool_manager.run_in_custom_threadpool(extract_skills_from_text, data.text)
        except ModelInferenceError as e:
            logger.error(f"Model inference error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract skills from text"
            )
        except Exception as e:
            logger.error(f"Unexpected error during skill extraction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during skill extraction"
            )

        if not skills:
            logger.warning("No skills found in the provided text")
            return []

        # Ищем сопоставленные курсы в базе.
        try:
            response = await find_courses(skills)
        except DatabaseError as e:
            logger.error(f"Database query error: {str(e)}")
            # Возвращаем навыки без курсов в случае ошибки БД
            response = [{"name": skill, "course": None} for skill in skills]
        except Exception as e:
            logger.error(f"Unexpected error during course lookup: {str(e)}")
            response = [{"name": skill, "course": None} for skill in skills]

        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled exception in get_skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/extract_skills_from_pdf", summary="Получить список навыков из полученного pdf")
async def get_skills_from_pdf(file: UploadFile = File(...)) -> List[SkillResponse]:
    """Принимает PDF, извлекает из него текст и возвращает навыки + курсы."""
    
    try:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is required"
            )

        if file.content_type not in ["application/pdf", "application/x-pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF document"
            )

        # Проверяем размер файла (максимум 50MB)
        max_size = 50 * 1024 * 1024
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File is too large (max 50MB)"
            )

        # Возвращаем файл в начебок для дальнейшего использования
        file.file.seek(0)

        try:
            text = await extract_text_from_pdf(file)
            if not text or len(text.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PDF contains no readable text"
                )
        except PDFExtractionError as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from PDF"
            )
        except Exception as e:
            logger.error(f"Unexpected error during PDF extraction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process PDF file"
            )

        try:
            skills = await threadpool_manager.run_in_custom_threadpool(extract_skills_from_text, text)
        except ModelInferenceError as e:
            logger.error(f"Model inference error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract skills from PDF text"
            )
        except Exception as e:
            logger.error(f"Unexpected error during skill extraction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during skill extraction"
            )

        if not skills:
            logger.warning("No skills found in the provided PDF")
            return []

        try:
            response = await find_courses(skills)
        except DatabaseError as e:
            logger.error(f"Database query error: {str(e)}")
            response = [{"name": skill, "course": None} for skill in skills]
        except Exception as e:
            logger.error(f"Unexpected error during course lookup: {str(e)}")
            response = [{"name": skill, "course": None} for skill in skills]

        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled exception in get_skills_from_pdf: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

