from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.middleware import AuthRateLimitMiddleware, CsrfProtectionMiddleware
from app.api.routes.auth import router as auth_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.app_name,
    description="CleverCrest AI backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CsrfProtectionMiddleware)
app.add_middleware(AuthRateLimitMiddleware)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "CleverCrest AI API is running",
        "environment": settings.app_env,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        database_result = result.scalar()

    return {
        "status": "healthy",
        "database": "connected",
        "result": database_result,
    }