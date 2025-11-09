# app/services/collection_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

import aioboto3
from aiobotocore.session import ClientCreatorContext as S3Client
from aiobotocore.response import StreamingBody

from sqlalchemy.future import select

from fastapi import UploadFile

import io
import zipfile

from app.models.dotfiles import Dotfile
from app.models.collections import Collection
from app.schemas.collections import CollectionCreate, CollectionContentAdd, CollectionContentRead

from app.services import file_storage_service
from app.services import dotfile_service

async def get_access_to_collection_for_user(db: AsyncSession, collection_id: int, user_id: int) -> bool:
    result = await db.execute(select(Collection).filter(Collection.id == collection_id))
    collection = result.scalars().first()

    if not collection:
        return False

    if not collection.is_private:
        return True

    user_is_owner = (collection.owner_id == user_id)

    return user_is_owner

async def get_collections_by_user_id(db: AsyncSession, user_id: int) -> Optional[list[Collection]]:
    result = await db.execute(select(Collection).filter(Collection.owner_id == user_id))
    return result.scalars().all()

async def create_collection(db: AsyncSession, collection: CollectionCreate, user_id: int) -> Collection:
    db_collection = Collection(name=collection.name, description=collection.description, is_private=collection.is_private, owner_id=user_id)
    db.add(db_collection)

    await db.commit()
    await db.refresh(db_collection)

    return db_collection

async def add_to_collection(db: AsyncSession, s3: S3Client, collection_add: CollectionContentAdd, files: list[UploadFile]) -> list[Dotfile]:
    # upload the files to s3 bucket
    for file in files:
        # Generate unique filename for storage
        storage_filename = dotfile_service.generate_dotfile_name_in_collection(collection_add.collection_id, file.filename)
        
        # Temporarily change the filename for storage
        original_filename = file.filename
        file.filename = storage_filename
        
        await file_storage_service.upload_file_to_storage(s3, file)
        
        # Restore original filename
        file.filename = original_filename

    result = await dotfile_service.create_dotfiles_in_collection(db, collection_add.content, collection_add.collection_id)

    return result

async def get_dotfile_paths_from_collection(db: AsyncSession, collection_id: int) -> list[Dotfile]:
    result = await dotfile_service.get_dotfiles_by_collection_id(db, collection_id)

    return result

async def get_dotfiles_from_collection(db: AsyncSession, s3: S3Client, collection_read: CollectionContentRead) -> bytes:
    db_dotfiles = await dotfile_service.get_dotfiles_by_collection_id(db, collection_read.collection_id)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zipper:
        for dotfile in db_dotfiles:
            filename = dotfile_service.generate_dotfile_name_in_collection(collection_read.collection_id, dotfile.filename)
            file = await file_storage_service.retrieve_file_from_storage_by_filename(s3, filename)

            content = file.read()
            zipper.writestr(filename, content)

    return zip_buffer.getvalue()

async def delete_from_collection(db: AsyncSession, s3: S3Client, collection_id: int, filename: str):
    deleted_filename = dotfile_service.generate_dotfile_name_in_collection(collection_id, filename)
    
    await file_storage_service.delete_file_from_storage_by_filename(s3, deleted_filename)
    await dotfile_service.delete_dotfile(db, deleted_filename)

    return

async def delete_collection(db: AsyncSession, s3: S3Client, collection_id: int):
    # Delete the dotfiles of the collection from the database and s3 buckets 
    db_dotfiles = await dotfile_service.get_dotfiles_by_collection_id(db, collection_id)

    for dotfile in db_dotfiles:
        deleted_filename = dotfile_service.generate_dotfile_name_in_collection(collection_id, dotfile.filename)
        await file_storage_service.delete_file_from_storage_by_filename(s3, deleted_filename)
        await dotfile_service.delete_dotfile(db, deleted_filename)

    # Delete the collection from the database
    db_collection = (await db.execute(select(Collection).filter(Collection.id == collection_id))).scalars().first()
    
    if db_collection:
        await db.delete(db_collection)
        await db.commit()

    return
    

# TO DO: Add update collection content function (Requires communication with front-end team)