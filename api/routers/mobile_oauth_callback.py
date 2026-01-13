"""Mobile OAuth callback handler - redirects to app with JWT token.

Uses RedirectResponse for ASWebAuthenticationSession compatibility.
ASWebAuthenticationSession (iOS 12+) natively handles redirects to custom URL schemes.
"""

import logging
from datetime import timedelta
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
import urllib.parse

from config import settings
from middleware.auth import create_access_token
from services import github

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/mobile-callback")
async def mobile_callback(
    code: str = Query(..., description="OAuth authorization code from GitHub"),
) -> RedirectResponse:
    """
    Mobile OAuth callback - redirects to app with JWT token.

    Flow:
    1. GitHub redirects here after user authorizes
    2. Exchange code for GitHub access token
    3. Create JWT with user info
    4. Redirect to rlog://oauth/callback?token=...
    5. ASWebAuthenticationSession on iOS catches the redirect
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

        # Build deep link URL and redirect
        # Note: GitHub returns None for email/avatar if not set, so we use 'or' to ensure strings
        email = user_data.get("email") or ""
        avatar_url = user_data.get("avatar_url") or ""

        deep_link = (
            f"rlog://oauth/callback"
            f"?token={urllib.parse.quote(access_token)}"
            f"&user_id={user_data['id']}"
            f"&username={urllib.parse.quote(user_data['login'])}"
            f"&email={urllib.parse.quote(email)}"
            f"&avatar_url={urllib.parse.quote(avatar_url)}"
        )

        return RedirectResponse(url=deep_link, status_code=302)

    except github.GitHubAPIError as e:
        logger.error(f"GitHub API Error: {e.message}")
        error_msg = urllib.parse.quote(f"GitHub OAuth failed: {e.message}")
        return RedirectResponse(
            url=f"rlog://oauth/callback?error={error_msg}",
            status_code=302,
        )

    except Exception as e:
        logger.exception(f"Unexpected error during OAuth: {e}")
        error_msg = urllib.parse.quote(f"Authentication failed: {str(e)}")
        return RedirectResponse(
            url=f"rlog://oauth/callback?error={error_msg}",
            status_code=302,
        )
