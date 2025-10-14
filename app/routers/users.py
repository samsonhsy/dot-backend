# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.users import UserCreate, UserOutput
from app.schemas.token import Token
from app.services import user_service
from app.core.security import create_access_token, verify_pwd

router = APIRouter()

@router.get("/", response_model=list[UserOutput])
async def user_list(db:AsyncSession = Depends(get_db)):
    db_users = await user_service.get_users(db)
    return db_users
    
# get me info

@router.delete("/{user_id}")
async def user_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await user_service.delete_user(db, user_id)
    return {"message": "User deleted"}
    
@router.post("/register", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user_by_email = await user_service.get_user_by_email(db=db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = await user_service.get_user_by_username(db=db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return await user_service.create_user(db=db, user=user)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user_by_username(db=db, username=form_data.username)
    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}