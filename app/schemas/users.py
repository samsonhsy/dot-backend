# app/schemas/users.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    username: str
    email: EmailStr
    
    class Config: 
        from_attributes = True # SQLAlchemy(DB) to Pydantic(API)