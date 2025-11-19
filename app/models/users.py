# app/models/users.py
from sqlalchemy import Column, Date, Integer, String, TIMESTAMP, func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True) # Can change to uuid later
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_pwd = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    account_tier = Column(String(50), default="free")
    monthly_retrieval_count = Column(Integer, default=0, nullable=False)
    retrieval_period_start_date = Column(Date, nullable=True, server_default=func.current_date())