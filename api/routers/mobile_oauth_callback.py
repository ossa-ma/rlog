"""Mobile OAuth callback handler - redirects to app with JWT token."""

from datetime import timedelta
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
import urllib.parse

from config import settings
from middleware.auth import create_access_token
from services import github


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/mobile-callback", response_class=HTMLResponse)
async def mobile_callback(
    code: str = Query(..., description="OAuth authorization code from GitHub"),
):
    """
    Mobile OAuth callback - redirects to app with JWT token.

    This endpoint handles OAuth for mobile apps:
    1. Receives code from GitHub
    2. Exchanges for access token
    3. Creates JWT
    4. Returns HTML with JavaScript to trigger deep link

    Flow:
    - GitHub redirects here after user authorizes
    - We exchange code for GitHub token
    - We create our own JWT
    - We return HTML that triggers rlog://oauth/callback?token=...
    - iOS app receives the deep link and extracts token + user info
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

        # Build deep link URL
        deep_link = (
            f"rlog://oauth/callback"
            f"?token={urllib.parse.quote(access_token)}"
            f"&user_id={user_data['id']}"
            f"&username={urllib.parse.quote(user_data['login'])}"
            f"&email={urllib.parse.quote(user_data.get('email', ''))}"
            f"&avatar_url={urllib.parse.quote(user_data.get('avatar_url', ''))}"
        )

        # Return HTML with JavaScript to trigger deep link
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting...</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #f5f5f7;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                }}
                h1 {{
                    color: #1d1d1f;
                    margin-bottom: 1rem;
                }}
                p {{
                    color: #86868b;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Login Successful</h1>
                <p>Returning to rlog...</p>
            </div>
            <script>
                // Trigger deep link immediately
                window.location.href = "{deep_link}";
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except github.GitHubAPIError as e:
        # Return HTML with error deep link
        error_msg = urllib.parse.quote(f"GitHub OAuth failed: {e.message}")
        error_link = f"rlog://oauth/callback?error={error_msg}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Error</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>Authentication Failed</h1>
            <p>{e.message}</p>
            <script>
                window.location.href = "{error_link}";
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        # Return HTML with generic error
        error_msg = urllib.parse.quote("Authentication failed")
        error_link = f"rlog://oauth/callback?error={error_msg}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Error</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>Authentication Failed</h1>
            <p>An error occurred during authentication.</p>
            <script>
                window.location.href = "{error_link}";
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
