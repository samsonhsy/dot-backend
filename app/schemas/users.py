# app/schemas/users.py
from typing import Literal
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    username: str
    email: EmailStr
    id: int
    account_tier: str
    class Config: 
        from_attributes = True # SQLAlchemy(DB) to Pydantic(API)

class UserPromote(BaseModel):
    user_id: int
    to_tier: Literal["free", "pro", "admin"] = "free"