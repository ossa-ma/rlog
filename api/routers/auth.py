"""GitHub OAuth authentication router.

Note: Token refresh not implemented. JWTs expire in 7 days - users re-auth via OAuth.
Future: Add refresh tokens if frequent re-authentication becomes friction point.
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from config import settings
from middleware.auth import create_access_token
from services import github


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class AuthURLResponse(BaseModel):
    """GitHub OAuth authorization URL."""

    auth_url: str


@router.get("/url", response_model=AuthURLResponse)
async def get_auth_url(
    redirect_uri: str | None = Query(None, description="Custom redirect URI (for mobile apps)")
) -> AuthURLResponse:
    """
    Get GitHub OAuth authorization URL.

    Frontend/mobile app redirects user to this URL to initiate OAuth flow.

    Args:
        redirect_uri: Optional custom redirect URI (e.g., 'rlog://oauth/callback' for iOS)
                     Defaults to web callback URL from settings

    Returns:
        GitHub OAuth URL with client_id and redirect_uri
    """
    # Use custom redirect URI if provided (for mobile), otherwise use default web URI
    final_redirect_uri = redirect_uri or settings.github_redirect_uri

    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={final_redirect_uri}"
        f"&scope=repo,user:email"
    )

    return AuthURLResponse(auth_url=auth_url)


@router.get("/callback", response_model=TokenResponse)
async def auth_callback(
    code: str = Query(..., description="OAuth authorization code from GitHub"),
) -> TokenResponse:
    """
    GitHub OAuth callback endpoint.

    Exchanges authorization code for access token and creates JWT.

    Args:
        code: OAuth authorization code from GitHub

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If OAuth exchange fails
    """
    try:
        # Exchange code for GitHub access token
        github_token = await github.exchange_code_for_token(
            code=code,
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
        )

        # Fetch user information
        user_data = await github.get_github_user(github_token)

        # Create JWT payload
        token_payload = {
            "user_id": user_data["id"],
            "username": user_data["login"],
            "email": user_data.get("email"),
            "avatar_url": user_data.get("avatar_url"),
            "github_token": github_token,
        }

        # Generate JWT
        access_token = create_access_token(
            data=token_payload, expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
        )

        return TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_expire_minutes * 60,
            user={
                "id": user_data["id"],
                "username": user_data["login"],
                "email": user_data.get("email"),
                "avatar_url": user_data.get("avatar_url"),
            },
        )

    except github.GitHubAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"GitHub OAuth failed: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )
