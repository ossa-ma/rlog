"""
rlog API - Backend service for reading log management.

Free tier features:
- GitHub OAuth authentication
- Reading log CRUD operations
- Automatic metadata fetching
- Commit to user's GitHub repository
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.routers import auth, reading, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 rlog API starting in {settings.environment} mode")
    print(f"📍 CORS origins: {settings.cors_origins_list}")

    yield

    # Shutdown
    print("👋 rlog API shutting down")


# Create FastAPI application
app = FastAPI(
    title="rlog API",
    description="Backend API for rlog - frictionless reading log service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    print(f"❌ Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if not settings.is_production else "An error occurred"
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(reading.router)


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "rlog API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs" if not settings.is_production else None,
        "github": "https://github.com/ossama/rlog",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production,
        log_level="info",
    )
