import uuid
from datetime import datetime
from sqlalchemy import select, delete
from auth_service.db import connection
from auth_service.models import User, UserSkill


@connection
async def get_existing_user(email: str, username: str, session):
    query = select(User).where(
        (User.email == email) | (User.username == username)
    )
    result = await session.execute(query)
    return result.scalars().first()


@connection
async def get_user_by_username(username: str, session):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalars().first()


@connection
async def get_user_by_id(user_id: str, session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None

    query = select(User).where(User.id == user_uuid)
    result = await session.execute(query)
    return result.scalars().first()


@connection
async def create_user(email: str, username: str, password_hash: str, full_name: str, session):
    user = User(
        email=email,
        username=username,
        password_hash=password_hash,
        full_name=full_name,
    )
    session.add(user)
    await session.commit()
    return user


@connection
async def update_user_last_login(user_id: str, session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None

    query = select(User).where(User.id == user_uuid)
    result = await session.execute(query)
    user = result.scalars().first()
    if user is None:
        return None

    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    return user


@connection
async def update_user_resume(user_id: str, resume: str | None, session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None

    query = select(User).where(User.id == user_uuid)
    result = await session.execute(query)
    user = result.scalars().first()
    if user is None:
        return None

    cleaned_resume = resume.strip() if isinstance(resume, str) and resume.strip() else None
    user.resume = cleaned_resume
    session.add(user)
    await session.commit()
    return user


@connection
async def update_user_profile(user_id: str, email: str, username: str, full_name: str | None, session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None, "User not found"

    cleaned_username = username.strip()
    if len(cleaned_username) < 3:
        return None, "Username must contain at least 3 characters"

    query = select(User).where(User.id == user_uuid)
    result = await session.execute(query)
    user = result.scalars().first()
    if user is None:
        return None, "User not found"

    conflict_query = select(User).where(
        ((User.email == email) | (User.username == cleaned_username)) & (User.id != user_uuid)
    )
    conflict_result = await session.execute(conflict_query)
    conflict = conflict_result.scalars().first()
    if conflict:
        if conflict.email == email:
            return None, "Email is already registered"
        return None, "Username is already registered"

    cleaned_name = full_name.strip() if isinstance(full_name, str) and full_name.strip() else None
    user.email = str(email)
    user.username = cleaned_username
    user.full_name = cleaned_name
    session.add(user)
    await session.commit()
    return user, None


@connection
async def update_user_skills(user_id: str, skills: list[str], session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return []

    cleaned_skills = []
    for skill in skills:
        if isinstance(skill, str):
            cleaned = skill.strip()
            if cleaned:
                cleaned_skills.append(cleaned)

    await session.execute(delete(UserSkill).where(UserSkill.user_id == user_uuid))

    for skill in sorted(set(cleaned_skills)):
        session.add(UserSkill(user_id=user_uuid, skill=skill))

    await session.commit()

    query = select(UserSkill.skill).where(UserSkill.user_id == user_uuid).order_by(UserSkill.skill.asc())
    result = await session.execute(query)
    return result.scalars().all()


@connection
async def get_user_skills(user_id: str, session):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return []

    query = select(UserSkill.skill).where(UserSkill.user_id == user_uuid).order_by(UserSkill.skill.asc())
    result = await session.execute(query)
    return result.scalars().all()
