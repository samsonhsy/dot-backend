# app/services/file_storage_service.py
import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from fastapi import UploadFile, HTTPException
from app.s3.s3_bucket import BUCKET_NAME

async def upload_file_to_storage(s3 : S3Client, file : UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="Uploaded file does not exist")

    result = await s3.put_object(Body=file, Bucket=BUCKET_NAME, Key=file.filename)

    return result  

async def retrieve_file_from_storage_by_filename(s3 : S3Client, filename : str):
    result = await s3.get_object(Bucket=BUCKET_NAME, Key=filename)

    if not result:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return result["Body"] 

async def delete_file_from_storage_by_filename(s3 : S3Client, filename : str):
    result = await s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    
    return result