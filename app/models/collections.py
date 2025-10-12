# app/models/collections.py
from sqlite3.dbapi2 import Timestamp
from sqlalchemy import Boolean, ForeignKey, Text, Column, Integer, String, TIMESTAMPTZ, func
from app.db.database import Base

class Collections(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_private = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMPTZ, server_default=func.now())
    updated_at = Column(TIMESTAMPTZ, server_default=func.now())

                