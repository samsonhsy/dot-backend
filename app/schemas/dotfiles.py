# app/schemas/dotfiles.py
from pydantic import BaseModel

class DotfileCreate(BaseModel):
    path : str
    filename : str

class DotfileOutput(BaseModel):
    path: str
    filename: str

    class Config:
        from_attributes = True