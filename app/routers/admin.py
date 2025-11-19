# # app/routers/admin_key.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.users import UserPromote
from app.services.license_key_service import create_keys, get_all_license_key, get_license_key_by_id
from app.schemas.license_key import KeyGenerationRequest, KeyGenerationResponse
from app.services.user_service import get_user_by_id
from app.schemas.license_key import LicenseKeyOutput

router = APIRouter()

@router.get("/license", response_model=list[LicenseKeyOutput], status_code=status.HTTP_200_OK)
async def list_license_keys(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all license keys.
    """
    db_license_keys = await get_all_license_key(db)

    return db_license_keys

@router.post("/license", response_model=KeyGenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_license_keys(request: KeyGenerationRequest, db: AsyncSession = Depends(get_db)):
    """
    Create multiple license keys and return them.
    """
    generated_keys = await create_keys(db, request.quantity)
    
    return KeyGenerationResponse(generated_keys=generated_keys)

@router.delete("/license/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license_key(key_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a license key by its ID.
    """
    license_key_exist = await get_license_key_by_id(db, key_id)
    if not license_key_exist:
        raise HTTPException(status_code=404, detail="License key not found")
    
    await db.delete(license_key_exist)
    await db.commit()
    return

@router.post("/promote-user", status_code=status.HTTP_200_OK)
async def promote_user(
    request: UserPromote,
    db: AsyncSession = Depends(get_db),
):
    """
    Promote a user to new tier by user ID.
    """
    db_user = await get_user_by_id(db, request.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Extract current values immediately to avoid lazy loading issues
    user_id = db_user.id
    username = db_user.username
    current_tier = db_user.account_tier
    
    # Check if already at target tier
    if current_tier == request.to_tier:
        raise HTTPException(
            status_code=400, 
            detail=f"User {username} is already in {request.to_tier} tier"
        )
    
    # Update the user's tier
    db_user.account_tier = request.to_tier
    
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user tier: {str(e)}"
        )
    
    # Return response immediately (no refresh needed since we use extracted values)
    return {
        "detail": f"User {username} promoted to {request.to_tier} tier successfully",
        "user_id": user_id,
        "username": username,
        "new_tier": request.to_tier
    }