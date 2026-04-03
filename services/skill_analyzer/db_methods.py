from sqlalchemy import select
from skill_analyzer.models import Skill
from skill_analyzer.db import connection
from skill_analyzer.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


@connection
async def find_skills_in_db(data_skills: list, session):
    """Find skills in database by name.
    
    Args:
        data_skills: List of skill names to search for
        session: SQLAlchemy async session
        
    Returns:
        Query result with matching skills
        
    Raises:
        DatabaseError: If database query fails
    """
    try:
        if not data_skills:
            return []
        
        query = select(Skill).filter(Skill.name.in_(data_skills))
        result = await session.execute(query)
        return result.scalars()
    except Exception as e:
        logger.error(f"Error querying skills from database: {str(e)}")
        raise DatabaseError(f"Failed to query skills from database: {str(e)}")