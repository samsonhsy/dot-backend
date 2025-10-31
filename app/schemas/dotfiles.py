# app/schemas/dotfiles.py
from pydantic import BaseModel, FilePath

class DotfileCreate(BaseModel):
    path : FilePath
    file_name : str

class DotfileOutput(BaseModel):
    path: FilePath
    file_name: str

    class Config:
        from_attributes = True