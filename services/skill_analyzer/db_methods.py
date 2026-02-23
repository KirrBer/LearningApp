from sqlalchemy import select
from models import Skill
from db import connection


@connection
async def find_skills(data_skills: list, session):
    query = select(Skill).filter(Skill.name.in_(data_skills))
    result = await session.execute(query)
    return result.scalars()