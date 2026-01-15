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

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import logging

from config import settings
from routers import auth, reading, health, mobile_oauth_callback
from utils.logging_config import setup_logging, request_id

# Setup structured logging
setup_logging()
log = logging.getLogger("rlog.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    log.info(f"rlog API starting in {settings.environment} mode")
    log.info(f"CORS origins: {settings.cors_origins_list}")

    yield

    log.info("rlog API shutting down")


# Create FastAPI application
app = FastAPI(
    title="rlog API",
    description="Backend API for rlog - frictionless reading log service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,
)


# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id_val = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id.set(request_id_val)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id_val
            return response
        finally:
            request_id.reset(token)


app.add_middleware(RequestIDMiddleware)

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
    log.error(f"Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if not settings.is_production else "An error occurred",
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(mobile_oauth_callback.router)
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
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production,
        log_level="info",
    )
