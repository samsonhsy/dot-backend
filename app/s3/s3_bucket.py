import boto3
from app.core.settings import settings

session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=settings.FILE_STORAGE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.FILE_STORAGE_SECRET_ACCESS_KEY,
    endpoint_url=settings.FILE_STORAGE_URL,
    region_name=settings.FILE_STORAGE_REGION
)

async def get_s3_client():
    return s3_client