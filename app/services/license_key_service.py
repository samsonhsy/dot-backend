# app/services/license_key_service.py
from datetime import date, timedelta
import secrets
import string
from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.models.license_keys import LicenseKey
from app.services.auth_service import get_current_user

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
        keys.append({"key_string": key_str})

        db_obj = LicenseKey(key_string=key_str)
        db.add(db_obj)
        db_objs.append(db_obj)

    if db_objs:
        await db.commit()

        for obj in db_objs:
            await db.refresh(obj)

    return keys

# Get license key from db
async def get_license_key_by_string(db: AsyncSession, key_string: str) -> LicenseKey:
    result = await db.execute(
        select(LicenseKey).filter(LicenseKey.key_string == key_string)
    )
    return result.scalars().first()

# Refresh retrieval period
async def refresh_retrieval_period(db: AsyncSession, user):
    period_end_date = user.retrieval_period_start_date + timedelta(days=settings.RETRIEVAL_PERIOD_DAYS)
    if date.today() > period_end_date:
        user.monthly_retrieval_count = 0
        user.retrieval_period_start_date = date.today()
        await db.commit()
        await db.refresh(user)
    return

