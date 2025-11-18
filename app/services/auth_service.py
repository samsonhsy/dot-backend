# app/services/auth_service.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt


from app.core.settings import settings
from app.db.database import get_db
from app.models.users import User
from app.services.user_service import get_user_by_email
from app.core.security import verify_pwd
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def authenticate_user(email: str, pwd: str, db: AsyncSession) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_pwd(pwd, user.hashed_pwd):
        return None
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> User:
    if user.account_tier != "admin":
        # print("User is not admin:", user.account_tier)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )
    # print("User is admin:", user.email)
    return user