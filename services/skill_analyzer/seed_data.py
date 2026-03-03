import asyncio
import logging
from .settings import settings
from .models import Skill
from .db import async_session_maker
from sqlalchemy import select


logger = logging.getLogger(__name__)

DATABASE_URL = settings.get_db_url()


async def seed_skills_with_models():
    """Заполнение навыков используя модели SQLAlchemy"""
    SKILLS_DATA = [
        {"name": "JavaScript", "course": "https://metanit.com/web/javascript"},
        {"name": "TypeScript", "course": "https://metanit.com/web/typescript"},
        {"name": "CSS", "course": "https://gist.github.com/dmitry-osin/c64f7d8eb9ed60cc932c4c56ac7eae22"},
        {"name": "PHP", "course": "https://metanit.com/php/tutorial"},
        {"name": "Git", "course": "https://proglib.io/p/git-for-half-an-hour"},
        {"name": "Python", "course": "https://metanit.com/python/tutorial/"},
    ]

    async with async_session_maker() as session:
        async with session.begin():
            for skill_data in SKILLS_DATA:

                query = select(Skill).where(Skill.name == skill_data["name"])
                result = await session.execute(query)
                existing = result.scalar_one_or_none()
                if not existing:
                    skill = Skill(**skill_data)
                    session.add(skill)
                    logger.info(f"✅ Добавлен навык: {skill_data['name']}")
                else:
                    existing.course = skill_data["course"]
                    logger.info(f"🔄 Обновлен навык: {skill_data['name']}")

async def main():
    try:
        await seed_skills_with_models()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())