# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.settings import settings

# Create the async engine
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

# Base class for models of database tables
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session