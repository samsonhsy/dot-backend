# app/routers/collections.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status, File, Form
from pydantic import ValidationError

import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.s3.s3_bucket import get_s3_client

from app.schemas.collections import CollectionCreate, CollectionContentRead, CollectionContentDelete, CollectionContentAdd, CollectionOutput
from app.schemas.dotfiles import DotfileOutput
from app.services import collection_service
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/owned", response_model=list[CollectionOutput])
async def get_my_collections(db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    '''Retrieves all collections owned by the current user'''
    return await collection_service.get_collections_by_user_id(db, user.id)

@router.post("/", response_model=CollectionOutput, status_code=status.HTTP_201_CREATED)
async def create_collection(collection : CollectionCreate, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    '''Creates a new collection owned by the current user'''
    db_collection = await collection_service.create_collection(db, collection, user.id)

    # Convert ORM object to Pydantic model so FastAPI/Swagger can serialize it reliably
    return CollectionOutput.model_validate(db_collection)

@router.post("/{collection_id}/dotfiles", response_model=list[DotfileOutput], status_code=status.HTTP_201_CREATED)
async def add_to_collection(
    collection_id:int,
    collection_add_payload: Annotated[
        str,
        Form(
            ...,
            description=(
                "JSON body describing each file, e.g. "
                "{\"collection_id\":3,\"content\":[{\"path\":\"/home/user/.zshrc\",\"filename\":\".zshrc\"},"
                "{\"path\":\"/home/user/.vimrc\",\"filename\":\".vimrc\"}]}"
            )
        )
    ],
    files: list[UploadFile] = File(
        ...,
        description="Upload files in the same order as content"
    ),
    db: AsyncSession = Depends(get_db),
    s3: S3Client = Depends(get_s3_client),
    user = Depends(get_current_user)
):
    """
    Add dotfiles to a collection.
    The 'content' list in the request body must match the 'files' list in order, 
    e.g. content[0] describes files[0]
    """
    try:
        collection_add = CollectionContentAdd.model_validate_json(collection_add_payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())

    # Ensure the body points to the same collection as the URL
    if collection_add.collection_id != collection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Body collection_id ({collection_add.collection_id}) must match URL collection_id ({collection_id})"
        )

    # Validate that files and content lists match
    if len(files) != len(collection_add.content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of files ({len(files)}) must match number of content entries ({len(collection_add.content)})"
        )
    
    # Validate that filenames match (to catch coordination errors)
    for i, (file, content) in enumerate(zip(files, collection_add.content)):
        if file.filename != content.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filename mismatch at index {i}: uploaded file is '{file.filename}' but content specifies '{content.filename}'"
            )

    # Check if collection exists
    collection_exists = await collection_service.get_collection_by_id(db, collection_id)
    if not collection_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {collection_id} not found")

    # Check if user has access
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_id, user.id)
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this collection")

    result = await collection_service.add_to_collection(db, s3, collection_add, files)

    return [DotfileOutput.model_validate(dotfile) for dotfile in result]

@router.get("/{collection_id}/archive")
async def get_collection_content(collection_id:int, db: AsyncSession = Depends(get_db), s3: S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    '''Retrieves all dotfiles from a collection as a zip archive'''
    # GET requests cannot have a body; construct the read model from the path param instead
    collection = CollectionContentRead(collection_id=collection_id)

    # Check if collection exists
    collection_exists = await collection_service.get_collection_by_id(db, collection_id)
    if not collection_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {collection_id} not found")

    # Check if user has access
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_id, user.id)
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this collection")

    zipfile = await collection_service.get_dotfiles_from_collection(db, s3, collection)

    headers = {"Content-Disposition": "attachment; filename=files.zip"}
    media_type = "application/zip"

    return Response(content=zipfile, headers=headers, media_type=media_type)

@router.get("/{collection_id}/dotfiles", response_model=list[DotfileOutput])
async def get_collection_file_paths(collection_id:int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    '''Retrieves all dotfiles from a collection'''
    # Check if collection exists
    collection_exists = await collection_service.get_collection_by_id(db, collection_id)
    if not collection_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {collection_id} not found")

    # Check if user has access
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_id, user.id)
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this collection")

    result = await collection_service.get_dotfile_from_collection(db, collection_id)

    return result

@router.delete("/{collection_id}/dotfiles/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_in_collection(collection_id:int, filename:str, db: AsyncSession = Depends(get_db), s3 : S3Client = Depends(get_s3_client), user = Depends(get_current_user)):
    '''Deletes a dotfile from a collection'''
    # Check if collection exists
    collection_exists = await collection_service.get_collection_by_id(db, collection_id)
    if not collection_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {collection_id} not found")
    
    # Check if user has access
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_id, user.id)
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this collection")

    await collection_service.delete_from_collection(db, s3, collection_id, filename)

    return

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_id:int, db: AsyncSession = Depends(get_db), s3 : S3Client = Depends(get_s3_client), user = Depends(get_current_user)):    
    '''Deletes an entire collection'''
    # Check if collection exists
    collection_exists = await collection_service.get_collection_by_id(db, collection_id)
    if not collection_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {collection_id} not found")
    
    # Check if user has access
    user_has_access = await collection_service.get_access_to_collection_for_user(db, collection_id, user.id)
    if not user_has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this collection")

    await collection_service.delete_collection(db, s3, collection_id)

    return