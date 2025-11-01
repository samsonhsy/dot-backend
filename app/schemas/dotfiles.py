# app/schemas/dotfiles.py
from pydantic import BaseModel, FilePath

class DotfileCreate(BaseModel):
    path : FilePath
    filename : str

class DotfileOutput(BaseModel):
    path: FilePath
    filename: str

    class Config:
        from_attributes = True