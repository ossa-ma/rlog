"""Health check router."""

from fastapi import APIRouter
from pydantic import BaseModel

from config import settings


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns basic service status and environment.
    """
    return HealthResponse(
        status="healthy",
        environment=settings.environment
    )
