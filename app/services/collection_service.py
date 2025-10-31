# app/services/collection_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from aiobotocore.response import StreamingBody

from sqlalchemy.future import select

from fastapi import UploadFile

from app.models.dotfiles import Dotfile
from app.models.collections import Collection
from app.schemas.collections import CollectionCreate, CollectionContentAdd, CollectionContentRead, CollectionContentDelete

from app.services import file_storage_service
from app.services import dotfile_service

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

async def add_to_collection(db: AsyncSession, s3: S3Client, collection_add: CollectionContentAdd, files: list[UploadFile]) -> list[Dotfile]:
    # upload the files to s3 bucket
    for file in files:
        file.filename = dotfile_service.generate_dotfile_name_in_collection(collection_add.collection_id, collection_add.filename)
        
        await file_storage_service.upload_file_to_storage(s3, file)

    result = await dotfile_service.create_dotfiles_in_collection(db, collection_add.content, collection_add.collection_id)

    return result

async def get_dotfiles_from_collection(db: AsyncSession, s3: S3Client, collection_read: CollectionContentRead) -> [list[Dotfile], list[StreamingBody]]:
    db_dotfiles = await dotfile_service.get_dotfiles_by_collection_id(db, collection_read.collection_id)

    result = []

    for dotfile in db_dotfiles:
        filename = dotfile_service.generate_dotfile_name_in_collection(collection_read.collection_id, dotfile.filename)
        file = await file_storage_service.retrieve_file_from_storage_by_filename(s3, filename)

        result.append(file)

    return db_dotfiles, result

async def delete_from_collection(db: AsyncSession, s3: S3Client, collection_delete: CollectionContentDelete):
    deleted_filename = dotfile_service.generate_dotfile_name_in_collection(collection_delete.collection_id, collection_delete.filename)
    
    await file_storage_service.delete_file_from_storage_by_filename(s3, deleted_filename)
    await dotfile_service.delete_dotfile(db, deleted_filename)

    return

# TO DO: Add update collection content function (Requires communication with front-end team)