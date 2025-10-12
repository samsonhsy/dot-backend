from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db
from app.routers import auth

app = FastAPI(title="Dot-Backend API")

@app.get("/api/healthcheck")
async def healthcheck(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=500, 
                            detail="Database connection failed")
        return {"status": "ok", "database_status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, 
                            detail=f"Database connection error: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the dot-backend API!"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])