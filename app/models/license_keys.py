from sqlalchemy import (Column, Integer, String, Boolean,DateTime, ForeignKey, func)
from app.db.database import Base

class LicenseKey(Base):
    __tablename__ = "license_keys"
    id = Column(Integer, primary_key=True, index=True)
    key_string = Column(String(255), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, nullable=False, server_default="false")

    activated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    activated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())