# app/services/dotfile_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.dotfiles import Dotfile
from app.schemas.dotfiles import DotfileCreate

# renames a dotfile to include its collection id as a prefix
def generate_dotfile_name_in_collection(collection_id: int, filename: str):
    return f"c{collection_id}/{filename}"

# retrieves all dotfiles with a collection id
async def get_dotfiles_by_collection_id(db: AsyncSession, collection_id: int) -> list[Dotfile]:
    result = await db.execute(select(Dotfile).filter(Dotfile.collection_id == collection_id))
    return result.scalars().all()

# creates dotfile records in the dotfile table 
async def create_dotfiles_in_collection(db: AsyncSession, dotfiles : list[DotfileCreate]) -> list[Dotfile]:
    db_dotfiles = [] 
    
    for dotfile in dotfiles:
        db_dotfile = Dotfile(path=dotfile.path, filename=dotfile.filename)
        db_dotfiles.append(db_dotfile)
    db.add_all(db_dotfiles)

    await db.commit()
    # refresh all dotfile row entries created
    refresh_statement = (
    select(Dotfile)
    .where(Dotfile.id.in_([db_dotfile.id for db_dotfile in db_dotfiles]))
    .execution_options(populate_existing=True)
    )
    
    await db.execute(refresh_statement)
    return db_dotfiles

# deletes a dotfile record from the dotfile table
async def delete_dotfile(db: AsyncSession, filename: str):
    db_dotfile = (await db.execute(select(Dotfile).filter(Dotfile.filename == filename))).scalars().first()
    if db_dotfile:
        await db.delete(db_dotfile)
        await db.commit()
    return