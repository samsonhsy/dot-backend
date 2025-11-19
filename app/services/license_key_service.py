# app/services/license_key_service.py
from datetime import date, timedelta
import secrets
import string
from typing import Optional
from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.models.license_keys import LicenseKey
from app.schemas.license_key import LicenseKeyOutput

# Return a license key like AAAA-BBBB-CCCC-DDDD.
def generate_key_string() -> str:
    alphabet = string.ascii_uppercase + string.digits
    groups = []
    for _ in range(4):
        group = ''.join(secrets.choice(alphabet) for _ in range(4))
        groups.append(group)

    return '-'.join(groups)

# Creates multiple license keys and stores them in the database
async def create_keys(db: AsyncSession, num_keys: int) -> list[str]:
    keys = []
    db_objs = []

    for _ in range(num_keys):
        key_str = generate_key_string()
        keys.append(key_str)  # Append plain string

        db_obj = LicenseKey(key_string=key_str)
        db.add(db_obj)
        db_objs.append(db_obj)

    if db_objs:
        await db.commit()

        for obj in db_objs:
            await db.refresh(obj)

    return keys

# Get license key from db by string
async def get_license_key_by_string(db: AsyncSession, key_string: str) -> Optional[LicenseKey]:
    result = await db.execute(
        select(LicenseKey).filter(LicenseKey.key_string == key_string)
    )
    return result.scalars().first()

# Get license key from db by id
async def get_license_key_by_id(db: AsyncSession, key_id: str) -> Optional[LicenseKey]:
    result = await db.execute(
        select(LicenseKey).filter(LicenseKey.id == key_id)
    )
    return result.scalars().first()

async def get_all_license_key(db: AsyncSession) -> list[LicenseKeyOutput]:
    result = await db.execute(select(LicenseKey))
    license_keys = result.scalars().all()

    return [
        LicenseKeyOutput(
            id=license_key.id,
            key_string=license_key.key_string,
            is_active=not license_key.is_used,
            assigned_to_user_id=license_key.activated_by_user_id,
        )
        for license_key in license_keys
    ]

# Refresh retrieval period
async def refresh_retrieval_period(db: AsyncSession, user):
    period_end_date = user.retrieval_period_start_date + timedelta(days=settings.RETRIEVAL_PERIOD_DAYS)
    if date.today() > period_end_date:
        user.monthly_retrieval_count = 0
        user.retrieval_period_start_date = date.today()
        await db.commit()
        await db.refresh(user)
    return
    
