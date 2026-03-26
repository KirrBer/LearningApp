from job_service.db import connection
from job_service.models import Vacancy
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


@connection
async def get_all_vacancies(session):
    """
    Получает все вакансии из БД.
    
    Args:
        session: SQLAlchemy сессия (предоставляется декоратором @connection)
        
    Returns:
        Список всех вакансий
        
    Raises:
        Exception: При ошибке доступа к БД
    """
    try:
        query = select(Vacancy)
        result = await session.execute(query)
        vacancies = result.scalars().all()
        
        if not vacancies:
            logger.warning("В БД не найдено вакансий")
        else:
            logger.info(f"Успешно загружено {len(vacancies)} вакансий из БД")
        
        return vacancies
        
    except Exception as e:
        logger.error(f"Ошибка при получении вакансий из БД: {str(e)}")
        raise

@connection
async def get_vacancy_by_id(id: int, session):
    try:
        query = select(Vacancy).filter(Vacancy.id == id)
        result = await session.execute(query)
        vacancy = result.scalars().first() 
        if not vacancy:
            logger.warning("В БД не найдено вакансий")
            return None
        
        return vacancy
        
    except Exception as e:
        logger.error(f"Ошибка при получении вакансий из БД: {str(e)}")
        raise