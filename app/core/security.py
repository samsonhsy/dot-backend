# app/core/security
from datetime import timedelta, datetime, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Check if a password matches a hashed password
def verify_pwd(plain_pwd: str, hashed_pwd:str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

# Hash a plain text password
def get_pwd_hash(pwd: str) -> str:
    return pwd_context.hash(pwd)

# Create a JWT token for authenticated users
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_HOURS * 60)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt