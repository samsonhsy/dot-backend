# app/s3/s3_bucket.py
import aioboto3 # needed for aibotocore.session
import aiobotocore
from app.core.settings import settings

session = aiobotocore.session.get_session()

s3_client = session.create_client(
    service_name='s3',
    aws_access_key_id=settings.FILE_STORAGE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.FILE_STORAGE_SECRET_ACCESS_KEY,
    endpoint_url=settings.FILE_STORAGE_URL,
    region_name=settings.FILE_STORAGE_REGION
)

BUCKET_NAME = 'dot-s3'

async def get_s3_client():
   async with s3_client as s3:        
        return s3