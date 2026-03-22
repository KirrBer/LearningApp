import asyncio
import logging
from job_service.settings import settings
from job_service.models import Vacancy
from job_service.db import connection
from sqlalchemy import select
from api_hhru import get_vacancies_id, get_vacancy


logger = logging.getLogger(__name__)

DATABASE_URL = settings.get_db_url()

@connection
async def seed_skills_with_models(session):
    """Заполнение навыков используя модели SQLAlchemy"""
    ids = get_vacancies_id()
    for id in ids:
        vacancy_data = get_vacancy(id)
        query = select(Vacancy).where(Vacancy.name == vacancy_data["name"])
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        if not existing:
            vacancy = Vacancy(**vacancy_data)
            session.add(vacancy)
            session.commit()
    logger.info("данные успешно добавлены или обновлены в базе данных")