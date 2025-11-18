# app/services/user_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import get_pwd_hash

async def get_users(db: AsyncSession) -> Optional[list[User]]:
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_pwd = get_pwd_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_pwd=hashed_pwd)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    db_user = (await db.execute(select(User).filter(User.id == user_id))).scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return
