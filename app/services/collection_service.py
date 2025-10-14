# app/services/collection_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.collections import Collection
from app.schemas.collections import CollectionCreate

from app.services.dotfile_service import create_dotfiles_in_collection

async def get_collections_by_user(db: AsyncSession, user_id: int) -> list[Collection]:
    result = await db.execute(select(Collection).filter(Collection.owner_id == user_id))
    return result.scalars().all()

async def create_collection(db: AsyncSession, collection: CollectionCreate, user_id: int) -> Collection:
    db_collection = Collection(name=collection.name, description=collection.description, owner_id=user_id)
    db.add(db_collection)

    await db.commit()
    await db.refresh(db_collection)

    await create_dotfiles_in_collection(db=db, collection_id=db_collection.id, dotfiles=collection.content)

    return db_collection