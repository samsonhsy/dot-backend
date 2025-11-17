# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.users import UserCreate, UserOutput
from app.schemas.token import Token
from app.services import user_service
from app.services.auth_service import get_current_user, oauth2_scheme

router = APIRouter()

@router.get("/", response_model=list[UserOutput], status_code=status.HTTP_200_OK)
async def user_list(db:AsyncSession = Depends(get_db)):
    '''Retrieves a list of all users'''
    db_users = await user_service.get_users(db)
    return db_users
    
@router.get("/me", response_model=UserOutput, status_code=status.HTTP_200_OK)
async def current_user_info(
    user = Depends(get_current_user)
):
    '''Retrieves information about the current authenticated user'''
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    '''Deletes a user by user ID'''
    db_user = await user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await user_service.delete_user(db, user_id)
    return 
    
@router.post("/register", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    '''Registers a new user'''
    db_user_by_email = await user_service.get_user_by_email(db=db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = await user_service.get_user_by_username(db=db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return await user_service.create_user(db=db, user=user)
