# app/services/collection_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.collections import Collection
from app.schemas.collections import CollectionCreate

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

    await create_dotfiles_in_collection(db=db, collection_id=db_collection.id, dotfiles=collection.content)

    return db_collection