# app/models/users.py
from sqlite3.dbapi2 import Timestamp
from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True) # Can change to uuid later
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_pwd = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
                