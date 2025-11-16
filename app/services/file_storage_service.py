# app/services/file_storage_service.py
import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from fastapi import UploadFile, HTTPException
from app.s3.s3_bucket import BUCKET_NAME

# uploads a file to S3 bucket
async def upload_file_to_storage(s3 : S3Client, file : UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="Uploaded file does not exist")

    file_contents = await file.read()
    if file_contents is None:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = await s3.put_object(Body=file_contents, Bucket=BUCKET_NAME, Key=file.filename)

    # Reset pointer so the caller can re-read the file if needed
    await file.seek(0)

    return result  

# retrieves a file from S3 bucket by filename
async def retrieve_file_from_storage_by_filename(s3 : S3Client, filename : str):
    result = await s3.get_object(Bucket=BUCKET_NAME, Key=filename)

    if not result:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return result["Body"] 

# deletes a file from S3 bucket by filename
async def delete_file_from_storage_by_filename(s3 : S3Client, filename : str):
    result = await s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    
    return result