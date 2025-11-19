# app/schemas/license_key.py
from pydantic import BaseModel, Field

class LicenseKeyActivate(BaseModel):
    key_string: str

class LicenseKeyOutput(BaseModel):
    id: int
    key_string: str
    is_active: bool
    assigned_to_user_id: int | None

class KeyGenerationResponse(BaseModel):
    generated_keys: list[str]

class KeyGenerationRequest(BaseModel):
    # at least 1 key, max 100 at a time.
    quantity: int = Field(..., gt=0, le=100)
