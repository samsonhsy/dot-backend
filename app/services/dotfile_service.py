# app/services/dotfile_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.dotfiles import Dotfile
from app.schemas.dotfiles import DotfileCreate

async def create_dotfiles_in_collection(db: AsyncSession, dotfiles : list[DotfileCreate], collection_id : int) -> list[Dotfile]:
    db_dotfiles = [Dotfile(path=dotfile.path, content=dotfile.content, collection_id=collection_id) for dotfile in dotfiles]
        
    db.add_all(db_dotfiles)

    await db.commit()
    
    # refresh all dotfile row entries created
    refesh_statement = (
    select(Dotfile)
    .where(Dotfile.path.in_([db_dotfile.path for db_dotfile in db_dotfiles]))
    .execution_options(populate_existing=True)
    )
    
    await db.execute(refesh_statement)

    return db_dotfiles