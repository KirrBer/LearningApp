"""Маршруты API для Job Service.

Здесь зарегистрированы endpoint-ы, которые отвечают за работу с вакансиями.
"""

from fastapi import APIRouter, Body, File, UploadFile
from job_service.utils import recommendations_sort, extract_text_from_pdf
from job_service.schemas import ResumeRequest, VacancyResponse
from typing import List

router = APIRouter()  # TODO: добавить реальные роуты (GET/POST и т.п.)

@router.post("/recommendations_from_text", summary="Получить список навыков из полученного текста")
async def get_recommendations(data: ResumeRequest = Body(...)) -> List[VacancyResponse]:
    response = await recommendations_sort(data.resume)
    return response

@router.post("/recommendations_from_pdf", summary="Получить список навыков из полученного текста")
async def get_recommendations(file: UploadFile = File(...)) -> List[VacancyResponse]:
    data = await extract_text_from_pdf(file)
    response = await recommendations_sort(data)
    return response