# app/schemas/dotfiles.py
from pydantic import BaseModel, FilePath

class DotfileCreate(BaseModel):
    path : FilePath
    content : str

class DotfileOutput(BaseModel):
    path: FilePath
    content: str

    class Config:
        from_attributes = True