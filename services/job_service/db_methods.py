from job_service.db import connection
from job_service.models import Vacancy
from sqlalchemy import select


@connection
async def get_all_vacancies(session):
    query = select(Vacancy)
    result = await session.execute(query)
    return result.scalars().all()