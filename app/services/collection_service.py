# app/services/collection_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client

from sqlalchemy.future import select

from fastapi import HTTPException, status, UploadFile

from app.models.dotfiles import Dotfile
from app.models.collections import Collection
from app.schemas.collections import CollectionCreate, CollectionContentAdd

from app.services import file_storage_service
from app.services.dotfile_service import create_dotfiles_in_collection

async def get_access_to_collection_for_user(db: AsyncSession, collection_id: int, user_id: int) -> bool:
    result = await db.execute(select(Collection).filter(Collection.id == collection_id))
    collection = result.scalars().first()

    if not collection.is_private:
        return True

    user_is_owner = (collection.owner_id == user_id)

    return user_is_owner

async def get_collections_by_user_id(db: AsyncSession, user_id: int) -> Optional[list[Collection]]:
    result = await db.execute(select(Collection).filter(Collection.owner_id == user_id))
    return result.scalars().all()

async def create_collection(db: AsyncSession, collection: CollectionCreate, user_id: int) -> Collection:
    db_collection = Collection(name=collection.name, description=collection.description, owner_id=user_id)
    db.add(db_collection)

    await db.commit()
    await db.refresh(db_collection)

    return db_collection

async def add_to_collection(db: AsyncSession, s3: S3Client, collection_add: CollectionContentAdd, files: list[UploadFile], user_id: int) -> list[Dotfile]:
    if not get_access_to_collection_for_user(db=db, collection_id=collection_add.collection_id, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have access to collection")
    
    # upload the files to s3 bucket
    for file in files:
        file.filename = f"{collection_add.collection_id}/{file.filename}"
        file_storage_service.upload_file_to_storage(s3, file)

    result = await create_dotfiles_in_collection(db, collection_add.content, collection_add.collection_id)

    return result

# TO DO: Add update collection content function (Requires communication with front-end team)