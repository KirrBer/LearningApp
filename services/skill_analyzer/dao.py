from sqlalchemy import select
from models import Skill
from db import async_session_maker


class SkillDAO:
    @classmethod
    async def find_skill(cls, data_skill: str):
        async with async_session_maker() as session:
            query = select(Skill).filter_by(name=data_skill)
            result = await session.execute(query)
            return result.scalar_one_or_none()