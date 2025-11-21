# tests/conftest.py
import pytest
import pytest_asyncio
import asyncio

import io
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

from fastapi.testclient import TestClient
from fastapi import UploadFile

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.s3.s3_bucket import get_s3_client, BUCKET_NAME

import aioboto3
from types_aiobotocore_s3 import S3Client

from main import app

from app.services.auth_service import get_current_admin_user
from app.models.users import User

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
async def mock_client(db_session, moto_patch_session):
    async def get_override_db():
        try:
            yield db_session
        finally:
            await db_session.close()
        
    async def get_override_s3_client():
        session = aioboto3.Session(region_name="us-east-1")
        async with session.client("s3", region_name="us-east-1") as s3_client:
            await s3_client.create_bucket(Bucket=BUCKET_NAME)

            yield s3_client

    # reset dependency overrides
    app.dependency_overrides = {}
    
    app.dependency_overrides[get_db] = get_override_db
    app.dependency_overrides[get_s3_client] = get_override_s3_client
  
    with TestClient(app) as mock_client:
        yield mock_client

@pytest_asyncio.fixture(scope="function")
async def mock_client_with_admin_tier(db_session, moto_patch_session):
    async def get_override_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    async def get_override_s3_client():
        session = aioboto3.Session(region_name="us-east-1")
        async with session.client("s3", region_name="us-east-1") as s3_client:
            await s3_client.create_bucket(Bucket=BUCKET_NAME)

            yield s3_client

    async def get_override_admin_user():
        return User(username="admin", email="admin@email.com", hashed_pwd="admin_password", account_tier="admin")

    # reset dependency overrides
    app.dependency_overrides = {}
    
    app.dependency_overrides[get_db] = get_override_db
    app.dependency_overrides[get_s3_client] = get_override_s3_client

    # remove admin tier check
    app.dependency_overrides[get_current_admin_user] = get_override_admin_user
  
    with TestClient(app) as mock_client:
        yield mock_client

@pytest.fixture()
def user_create_payload():
    return {
        "username":"mock_user",
        "email": "mock_email@email.com",
        "password": "mock_password"
    }

@pytest.fixture()
def key_generation_request():
    return {
        "quantity": 4
    }

@pytest.fixture()
def collection_create_payload():
    return {
        "name": "mock_collection",
        "description": "mock_collection_description",
        "is_private": False
    }

@pytest.fixture
def dotfiles_create_data():
    return [
        {
            "path": "/mock_dir/",
            "filename": ".mock0"
        },
        {
            "path": "/mock_dir/",
            "filename": ".mock1"
        }
    ]

@pytest.fixture
def collection_add_payload(dotfiles_create_data):
    return {
        "content": dotfiles_create_data
    }

@pytest.fixture()
def mock_files():
    headers = {"content-type": "text/plain"}
    file_0 = UploadFile(file=io.BytesIO(".mock0".encode("utf-8")), filename=".mock0", headers=headers)
    file_1 = UploadFile(file=io.BytesIO(".mock1".encode("utf-8")), filename=".mock1", headers=headers)
    
    return [("files", (file_0.filename, file_0.file)), ("files", (file_1.filename, file_1.file))]