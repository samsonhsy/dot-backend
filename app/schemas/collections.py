# app/schemas/collections.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.dotfiles import DotfileCreate

class CollectionCreate(BaseModel):
    name : str
    description : Optional[str] = ""
    is_private : Optional[bool] = True

class CollectionContentAdd(BaseModel):
    """Schema for adding dotfiles to a collection. 
    The content list should match the uploaded files list in order."""
    content : list[DotfileCreate]

class CollectionContentDelete(BaseModel):
    collection_id : int
    filename : str

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