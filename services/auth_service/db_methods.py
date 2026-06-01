import uuid
from datetime import datetime
from sqlalchemy import select
from auth_service.db import connection
from auth_service.models import User


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
