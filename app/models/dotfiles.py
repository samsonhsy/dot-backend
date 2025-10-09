# app/models/dotfiles.py
from sqlite3.dbapi2 import Timestamp
from sqlalchemy import Text, Column, Integer, String
from app.db.database import Base

class Dotfiles(Base):
    __tablename__ = "dotfiles"
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, nullable=False)
    path = Column(String(255), nullable=False) # Can change string length later
    content = Column(Text, nullable=False)
                