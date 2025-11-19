# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone


from app.db.database import get_db
from app.schemas.users import UserCreate, UserOutput
from app.services import user_service
from app.services.auth_service import get_current_user
from app.schemas.license_key import LicenseKeyActivate
from app.services.license_key_service import get_license_key_by_string

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

@router.post("/me/license-activate", status_code=status.HTTP_200_OK)
async def activate_license_key(
    license_data: LicenseKeyActivate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.account_tier == "admin":
        raise HTTPException(status_code=400, detail="Admin accounts don't need upgrade")

    if user.account_tier == "pro":
        raise HTTPException(status_code=400, detail="Account already upgraded to pro tier")
    
    key_in_db = await get_license_key_by_string(db, license_data.key_string)

    if not key_in_db or key_in_db.is_used:
        raise HTTPException(status_code=400, detail="Invalid or already used license key")
    
    # Activate the license key for the user
    db_user = await user_service.get_user_by_id(db=db, user_id=user.id)
    if not db_user:
        # Unexpected: the authenticated user should exist in the DB, but handle safely
        raise HTTPException(status_code=500, detail="Authenticated user not found in database")

    db_user.account_tier = "pro"
    key_in_db.is_used = True
    key_in_db.activated_by_user_id = db_user.id
    key_in_db.activated_at = datetime.now(timezone.utc)

    # Commit and refresh the DB-attached instances
    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to activate license key: {exc}") from exc

    await db.refresh(db_user)
    await db.refresh(key_in_db)

    return {"detail": "License key activated successfully, account upgraded to pro tier"}