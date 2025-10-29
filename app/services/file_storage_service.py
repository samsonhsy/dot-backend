# app/services/file_storage_service.py
import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from fastapi import UploadFile
from app.s3.s3_bucket import BUCKET_NAME

async def upload_file_to_storage(s3 : S3Client, file : UploadFile):
    await s3.put_object(Body=file, Bucket=BUCKET_NAME, Key=file.filename)  

async def retrieve_file_from_storage_by_filename(s3 : S3Client, filename : str):
    await s3.get_object(Bucket=BUCKET_NAME, Key=filename) 

async def delete_file_from_storage_by_filename(s3 : S3Client, filename : str):
    await s3.delete_object(Bucket=BUCKET_NAME, Key=filename)