import asyncio
import logging
from settings import settings
from models import Skill
from db import async_session_maker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = settings.get_db_url()


async def seed_skills_with_models():
    """Заполнение навыков используя модели SQLAlchemy"""
    SKILLS_DATA = [
        {"name": "JavaScript", "course": "https://metanit.com/web/javascript/"},
        {"name": "TypeScript", "course": "https://metanit.com/web/typescript/"},
        {"name": "Python", "course": "https://metanit.com/python/tutorial/"},
    ]

    async with async_session_maker() as session:
        async with session.begin():
            for skill_data in SKILLS_DATA:
                skill = Skill(**skill_data)
                session.add(skill)
                logger.info(f"✅ Добавлен навык: {skill_data['name']}")

async def main():
    try:
        await seed_skills_with_models()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())