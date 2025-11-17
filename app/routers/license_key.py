# # app/routers/license_key.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.license_key_service import create_keys
from app.schemas.license_key import KeyGenerationRequest, KeyGenerationResponse

router = APIRouter()

@router.post("/", response_model=KeyGenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_license_keys(request: KeyGenerationRequest, db: AsyncSession = Depends(get_db)):
    """
    Create multiple license keys and return them.
    """
    generated_keys = await create_keys(db, request.quantity)
    
    return KeyGenerationResponse(generated_keys=generated_keys)
