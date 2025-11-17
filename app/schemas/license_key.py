# app/schemas/license_key.py
from pydantic import BaseModel

class LicenseKeyActivate(BaseModel):
    key_string: str