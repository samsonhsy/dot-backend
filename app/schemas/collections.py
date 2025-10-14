# app/schemas/collections.py
from typing import Optional
from pydantic import BaseModel, datetime
from schemas.dotfiles import DotfileCreate

class CollectionCreate(BaseModel):
    name : str
    description : Optional[str] = ""
    is_private : Optional[bool] = True
    content : list[DotfileCreate]

class CollectionContentUpdate(BaseModel):
    collection_id : int
    content : list[DotfileCreate]

class CollectionContentRead(BaseModel):
    collection_id : int

class CollectionOutput(BaseModel):
    id : int
    name : str
    description : str
    updated_at : datetime
    created_at : datetime

    class Config:
        from_attributes = True