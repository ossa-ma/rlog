"""Mobile OAuth callback handler - redirects to app with JWT token."""

from datetime import timedelta
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
import urllib.parse

from config import settings
from middleware.auth import create_access_token
from services import github


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/mobile-callback")
async def mobile_callback(
    code: str = Query(..., description="OAuth authorization code from GitHub"),
):
    """
    Mobile OAuth callback - redirects to app with JWT token.

    This endpoint handles OAuth for mobile apps:
    1. Receives code from GitHub
    2. Exchanges for access token
    3. Creates JWT
    4. Redirects to custom URL scheme (rlog://) with token

    Flow:
    - GitHub redirects here after user authorizes
    - We exchange code for GitHub token
    - We create our own JWT
    - We redirect to rlog://oauth/callback?token=...&user_id=...&username=...
    - iOS app receives the URL and extracts token + user info
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

        # Redirect to mobile app with token and user info
        redirect_url = (
            f"rlog://oauth/callback"
            f"?token={urllib.parse.quote(access_token)}"
            f"&user_id={user_data['id']}"
            f"&username={urllib.parse.quote(user_data['login'])}"
            f"&email={urllib.parse.quote(user_data.get('email', ''))}"
            f"&avatar_url={urllib.parse.quote(user_data.get('avatar_url', ''))}"
        )

        return RedirectResponse(url=redirect_url)

    except github.GitHubAPIError as e:
        # Redirect to app with error
        error_msg = urllib.parse.quote(f"GitHub OAuth failed: {e.message}")
        return RedirectResponse(url=f"rlog://oauth/callback?error={error_msg}")

    except Exception as e:
        # Redirect to app with generic error
        error_msg = urllib.parse.quote("Authentication failed")
        return RedirectResponse(url=f"rlog://oauth/callback?error={error_msg}")
