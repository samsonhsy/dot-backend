# app/s3/s3_bucket.py
from collections.abc import AsyncGenerator

import aiobotocore
from aiobotocore.client import AioBaseClient
from botocore.config import Config
from app.core.settings import settings

BUCKET_NAME = 'dot-s3'

async def get_s3_client() -> AsyncGenerator[AioBaseClient, None]:
    config = Config(
        connect_timeout=10,
        read_timeout=60,
        retries={'max_attempts': 2}
    )
    
    # Create a new session for each request to avoid connection reuse issues
    session = aiobotocore.session.get_session()
    
    async with session.create_client(
        service_name='s3',
        aws_access_key_id=settings.FILE_STORAGE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.FILE_STORAGE_SECRET_ACCESS_KEY,
        endpoint_url=settings.FILE_STORAGE_URL,
        region_name=settings.FILE_STORAGE_REGION,
        config=config
    ) as s3_client:
        yield s3_client


async def check_storage_health() -> None:
    session = aiobotocore.session.get_session()
    async with session.create_client(
        service_name='s3',
        aws_access_key_id=settings.FILE_STORAGE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.FILE_STORAGE_SECRET_ACCESS_KEY,
        endpoint_url=settings.FILE_STORAGE_URL,
        region_name=settings.FILE_STORAGE_REGION
    ) as s3_client:
        await s3_client.head_bucket(Bucket=BUCKET_NAME)