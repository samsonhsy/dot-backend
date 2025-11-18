# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    FILE_STORAGE_URL : str
    FILE_STORAGE_ACCESS_KEY_ID : str
    FILE_STORAGE_SECRET_ACCESS_KEY : str
    FILE_STORAGE_REGION : str

    ACCESS_TOKEN_EXPIRE_HOURS: int
    SECRET_KEY: str
    ALGORITHM: str

    FREE_TIER_RETRIEVAL_LIMIT: int
    RETRIEVAL_PERIOD_DAYS: int

    model_config = SettingsConfigDict(env_file=".env") # Load settings from .env file
    

settings = Settings()
