# app/services/collection_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.collections import Collection
from schemas.collections import CollectionOutput

async def get_collections_by_user(db: AsyncSession, user_id: int) -> list[CollectionOutput]:
    result = await db.execute(select(Collection).filter(Collection.owner_id == user_id))
    return result.scalars().all()

async def create_collection(db: AsyncSession, collection: CollectionCreate, user_id: int) -> CollectionOutput:
    db_collection = Collection(name=collection.name, description=collection.description, owner_id=user_id)
    db.add(db_collection)

    await db.commit()
    await db.refresh(db_collection)

    # TO DO: Add create dotfiles related to collection function

    return db_collection