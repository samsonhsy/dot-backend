# app/routers/collections.py
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status

import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.s3.s3_bucket import get_s3_client

from app.schemas.collections import CollectionCreate, CollectionDelete, CollectionContentRead, CollectionContentDelete, CollectionContentAdd, CollectionOutput
from app.schemas.dotfiles import DotfileOutput
from app.services import collection_service
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/owned", response_model=list[CollectionOutput])
async def get_my_collections(db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await collection_service.get_collections_by_user_id(db, user.id)

@router.post("/create", response_model=CollectionOutput)
async def create_collection(collection : CollectionCreate, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await collection_service.create_collection(db, collection, user.id)

@router.post("/{collection_id}/add", response_model=list[DotfileOutput])
async def add_to_collection(collection_id:int, collection_add: CollectionContentAdd, files: list[UploadFile], db: AsyncSession = Depends(get_db), s3: S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    collection_add.collection_id = collection_id

    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_add.collection_id, user.id)
    
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permissions to access this collection.")

    result = await collection_service.add_to_collection(db, s3, collection_add, files)

    return result

@router.get("/{collection_id}/content")
async def get_collection_content(collection_id:int, collection : CollectionContentRead, db: AsyncSession = Depends(get_db), s3: S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    collection.collection_id = collection_id

    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection.collection_id, user.id)
    
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permissions to access this collection.")

    zipfile = await collection_service.get_dotfiles_from_collection(db, s3, collection)

    headers = {"Content-Disposition": "attachment; filename=files.zip"}
    media_type = "application/zip"

    return Response(content=zipfile, headers=headers, media_type=media_type)

@router.get("/{collection_id}/file-paths", response_model=list[DotfileOutput])
async def get_collection_file_paths(collection_id:int, collection : CollectionContentRead, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    collection.collection_id = collection_id

    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection.collection_id, user.id)
    
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permissions to access this collection.")

    result = await collection_service.get_dotfile_paths_from_collection(db, collection)

    return result

@router.delete("/{collection_id}/delete-file")
async def delete_file_in_collection(collection_id:int, collection_delete: CollectionContentDelete, db: AsyncSession = Depends(get_db), s3 : S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    collection_delete.collection_id = collection_id
    
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_delete.collection_id, user.id)
    
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permissions to access this collection.")

    await collection_service.delete_from_collection(db, s3, collection_delete)

    return {"message" : f"File deleted from collection {collection_delete.collection_id}"}

@router.delete("/{collection_id}/delete-collection")
async def delete_collection(collection_id:int, collection : CollectionDelete, db: AsyncSession = Depends(get_db), s3 : S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    collection.collection_id = collection_id
    
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection.collection_id, user.id)
    
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permissions to access this collection.")

    await collection_service.delete_collection(db, s3, collection)

    return {"message": f"Collection deleted"}