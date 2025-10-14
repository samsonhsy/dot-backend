# app/models/dotfiles.py
from sqlalchemy import ForeignKey, Text, Column, Integer, String
from app.db.database import Base

class Dotfile(Base):
    __tablename__ = "dotfiles"
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)
    path = Column(String(255), nullable=False) # Can change string length later
    content = Column(Text, nullable=False)
                