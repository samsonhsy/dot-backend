# app/models/dotfiles.py
from sqlalchemy import ForeignKey, Text, Column, Integer, String, UniqueConstraint
from app.db.database import Base

class Dotfile(Base):
    __tablename__ = "dotfiles"
    __table_args__ = (
        UniqueConstraint("collection_id", "path", name="dotfiles_collection_id_path_key"),
    )
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)
    path = Column(String(255), nullable=False) # Can change string length later
    filename = Column(String(255), nullable=False)
                