from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db
from app.routers import auth, users, collections
from app.s3.s3_bucket import check_storage_health

app = FastAPI(title="Punkt-Backend API")

@app.get("/api/healthcheck")
async def healthcheck(db: AsyncSession = Depends(get_db)):
    errors = {}

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one_or_none() is None:
            errors["database"] = "Database connection failed"
    except Exception as e:
        errors["database"] = f"Database connection error: {str(e)}"

    try:
        await check_storage_health()
    except Exception as e:
        errors["storage"] = f"Storage connection error: {str(e)}"

    if errors:
        raise HTTPException(status_code=500, detail=errors)

    return {
        "status": "ok",
        "database_status": "connected",
        "storage_status": "connected",
    }

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Punkt-backend API!"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(collections.router, prefix="/collections", tags=["Collections"])
