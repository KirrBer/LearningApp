import asyncio
import logging
from sqlalchemy import select
from job_service.models import Vacancy
from job_service.db import connection

logger = logging.getLogger(__name__)

DUMMY_VACANCIES = [
    {
        'id': 1001,
        'name': 'Junior Python Developer',
        'description': 'Разработка бэкенд-сервисов на Python, поддержка существующего кода, участие в командных задачах.',
        'employer': 'TechStart',
        'salary': 'от 60 000 до 90 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'Нет опыта',
        'area': 'Москва'
    },
    {
        'id': 1002,
        'name': 'Middle Java Developer',
        'description': 'Разработка микросервисов на Java, интеграция с внешними API, тестирование решения.',
        'employer': 'CloudSoft',
        'salary': 'от 120 000 до 170 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Гибкий график',
        'experience': 'От 3 лет',
        'area': 'Санкт-Петербург'
    },
    {
        'id': 1003,
        'name': 'Data Analyst',
        'description': 'Анализ данных, подготовка отчетов, работа с SQL и BI-инструментами.',
        'employer': 'InsightLab',
        'salary': 'от 90 000 до 130 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'От 1 года',
        'area': 'Новосибирск'
    },
    {
        'id': 1004,
        'name': 'Frontend Developer (React)',
        'description': 'Создание пользовательских интерфейсов на React, оптимизация клиентской части.',
        'employer': 'UIHouse',
        'salary': 'от 100 000 до 140 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Гибкий график',
        'experience': 'От 2 лет',
        'area': 'Казань'
    },
    {
        'id': 1005,
        'name': 'DevOps Engineer',
        'description': 'Автоматизация развёртывания, работа с Docker, Kubernetes и CI/CD.',
        'employer': 'InfraWorks',
        'salary': 'от 140 000 до 190 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'От 3 лет',
        'area': 'Москва'
    },
    {
        'id': 1006,
        'name': 'Product Manager',
        'description': 'Управление продуктом, работа с командой, формирование требований и приоритетов.',
        'employer': 'Productive',
        'salary': 'от 130 000 до 180 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Гибкий график',
        'experience': 'От 2 лет',
        'area': 'Москва'
    },
    {
        'id': 1007,
        'name': 'QA Engineer',
        'description': 'Тестирование веб-приложений, написание автотестов и ручное тестирование.',
        'employer': 'QualityFirst',
        'salary': 'от 80 000 до 110 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'От 1 года',
        'area': 'Санкт-Петербург'
    },
    {
        'id': 1008,
        'name': 'Mobile Developer (Android)',
        'description': 'Разработка мобильных приложений на Android, работа с Kotlin и Jetpack.',
        'employer': 'AppForge',
        'salary': 'от 110 000 до 150 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'От 2 лет',
        'area': 'Екатеринбург'
    },
    {
        'id': 1009,
        'name': 'UI/UX Designer',
        'description': 'Проектирование интерфейсов, создание прототипов, работа с дизайнерскими системами.',
        'employer': 'DesignLab',
        'salary': 'от 85 000 до 125 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Гибкий график',
        'experience': 'От 1 года',
        'area': 'Калининград'
    },
    {
        'id': 1010,
        'name': 'System Administrator',
        'description': 'Поддержка серверов, работа с сетью и инфраструктурой, мониторинг и резервное копирование.',
        'employer': 'SysGuard',
        'salary': 'от 70 000 до 100 000 ₽',
        'employment': 'Полная занятость',
        'schedule': 'Полный день',
        'experience': 'От 1 года',
        'area': 'Сочи'
    }
]


@connection
async def seed_vacancies(session):
    """Заполняет базу тестовыми вакансиями, без обращения к HH.ru API."""
    for vacancy_data in DUMMY_VACANCIES:
        query = select(Vacancy).where(Vacancy.id == vacancy_data['id'])
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            logger.info(f"Вакансия с id={vacancy_data['id']} уже существует, пропускаем")
            continue

        vacancy = Vacancy(**vacancy_data)
        session.add(vacancy)

    await session.commit()
    logger.info("Данные успешно добавлены в базу данных")


# Комментируем старую логику загрузки данных через HH.ru API.
# from job_service.api_hhru import get_vacancies_id, get_vacancy
#
# @connection
# async def seed_skills_with_models(session):
#     """Заполнение навыков используя модели SQLAlchemy"""
#     ids = []
#     for i in range(3):
#         ids += get_vacancies_id(page=i)
#     for id in ids:
#         time.sleep(1)
#         query = select(Vacancy).where(Vacancy.id == int(id))
#         result = await session.execute(query)
#         existing = result.scalar_one_or_none()
#         if not existing:
#             vacancy_data = get_vacancy(id)
#             if not vacancy_data:
#                 logger.warning(f"Вакансия с id {id} не найдена через API")
#                 continue
#             vacancy = Vacancy(**vacancy_data)
#             session.add(vacancy)
#             await session.commit()
#     logger.info("данные успешно добавлены или обновлены в базе данных")


asyncio.run(seed_vacancies())