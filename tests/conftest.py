# tests/conftest.py
import pytest
import pytest_asyncio
import asyncio

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from main import app

# in-memory temporary database for testing
MOCK_DATABASE_URL = "sqlite+aiosqlite:///"

# Create the async engine
engine = create_async_engine(
    MOCK_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

MockAsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_models():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

asyncio.run(init_models())

@pytest_asyncio.fixture(scope="function")
async def db_session():
    connection = await engine.connect()
    transaction = await connection.begin()

    session = MockAsyncSessionLocal(bind=connection)
    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest_asyncio.fixture(scope="function")
async def mock_client(db_session):
    async def get_override_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = get_override_db
    
    with TestClient(app) as mock_client:
        yield mock_client

@pytest.fixture()
def user_create_payload():
    return {
        "username":"mock_user",
        "email": "mock_email@email.com",
        "password": "mock_password"
    }