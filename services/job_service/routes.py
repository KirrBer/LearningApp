"""Маршруты API для Job Service.

Здесь зарегистрированы endpoint-ы, которые отвечают за работу с вакансиями.
"""

from fastapi import APIRouter, Body
from job_service.utils import recommendations_sort
from job_service.schemas import ResumeRequest, VacancyResponse
from typing import List

router = APIRouter()  # TODO: добавить реальные роуты (GET/POST и т.п.)

@router.post("/recommendations", summary="Получить список навыков из полученного текста")
async def get_recommendations(data: ResumeRequest = Body(...)) -> List[VacancyResponse]:
    response = recommendations_sort(data.resume)
    return response