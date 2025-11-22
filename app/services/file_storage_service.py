# app/services/file_storage_service.py
from aiobotocore.session import ClientCreatorContext as S3Client
from fastapi import UploadFile, HTTPException
import asyncio
import botocore
from app.s3.s3_bucket import BUCKET_NAME

# uploads a file to S3 bucket
async def upload_file_to_storage(s3 : S3Client, file : UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="Uploaded file does not exist")

    file_contents = await file.read()
    if file_contents is None:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = await asyncio.wait_for(
            s3.put_object(Body=file_contents, Bucket=BUCKET_NAME, Key=file.filename),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail=f"Storage upload timeout for {file.filename}")
    # Reset pointer so the caller can re-read the file if needed
    await file.seek(0)

    return result  

# retrieves a file from S3 bucket by filename
async def retrieve_file_from_storage_by_filename(s3 : S3Client, filename : str):
    try:
        result = await s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    except botocore.exceptions.ClientError as exc:
        # Translate S3 NoSuchKey into a 404 HTTP response for callers
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"File {filename} not found") from exc
        # re-raise other client errors as 500
        raise HTTPException(status_code=500, detail=f"Storage error: {exc}") from exc

    if not result:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return result["Body"]

# deletes a file from S3 bucket by filename
async def delete_file_from_storage_by_filename(s3 : S3Client, filename : str):
    result = await s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    
    return result