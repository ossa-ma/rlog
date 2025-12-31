"""GitHub API service for OAuth and repository operations."""

import json
import base64
from typing import Any
from datetime import datetime

import aiohttp


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> str:
    """
    Exchange OAuth code for GitHub access token.

    Args:
        code: OAuth authorization code from GitHub callback
        client_id: GitHub OAuth app client ID
        client_secret: GitHub OAuth app client secret

    Returns:
        GitHub access token

    Raises:
        GitHubAPIError: If token exchange fails
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        ) as response:
            if response.status != 200:
                raise GitHubAPIError(
                    f"Failed to exchange code for token: {response.status}",
                    status_code=response.status
                )

            data = await response.json()

            if "error" in data:
                raise GitHubAPIError(f"GitHub OAuth error: {data.get('error_description', data['error'])}")

            return data["access_token"]


async def get_github_user(access_token: str) -> dict[str, Any]:
    """
    Fetch authenticated user information from GitHub.

    Args:
        access_token: GitHub access token

    Returns:
        User information dictionary

    Raises:
        GitHubAPIError: If user fetch fails
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        ) as response:
            if response.status != 200:
                raise GitHubAPIError(
                    f"Failed to fetch user info: {response.status}",
                    status_code=response.status
                )

            return await response.json()


async def get_file_from_repo(
    owner: str,
    repo: str,
    path: str,
    branch: str,
    access_token: str
) -> dict[str, Any]:
    """
    Get file contents from GitHub repository.

    Args:
        owner: Repository owner username
        repo: Repository name
        path: File path in repository
        branch: Branch name
        access_token: GitHub access token

    Returns:
        File metadata including content and SHA

    Raises:
        GitHubAPIError: If file fetch fails
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            params={"ref": branch},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        ) as response:
            if response.status == 404:
                # File doesn't exist yet - return empty structure
                return {"content": None, "sha": None}

            if response.status != 200:
                raise GitHubAPIError(
                    f"Failed to fetch file from repo: {response.status}",
                    status_code=response.status
                )

            return await response.json()


async def commit_file_to_repo(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    access_token: str,
    sha: str | None = None
) -> dict[str, Any]:
    """
    Commit file to GitHub repository.

    Args:
        owner: Repository owner username
        repo: Repository name
        path: File path in repository
        content: File content (will be base64 encoded)
        message: Commit message
        branch: Branch name
        access_token: GitHub access token
        sha: Current file SHA (required for updates, None for new files)

    Returns:
        Commit response from GitHub

    Raises:
        GitHubAPIError: If commit fails
    """
    # Base64 encode content
    content_bytes = content.encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

    payload: dict[str, Any] = {
        "message": message,
        "content": content_b64,
        "branch": branch,
    }

    if sha:
        payload["sha"] = sha

    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        ) as response:
            if response.status not in (200, 201):
                error_data = await response.json()
                raise GitHubAPIError(
                    f"Failed to commit file: {error_data.get('message', 'Unknown error')}",
                    status_code=response.status
                )

            return await response.json()


async def update_reading_log(
    owner: str,
    repo: str,
    path: str,
    branch: str,
    new_entry: dict[str, Any],
    access_token: str,
    commit_message: str | None = None
) -> dict[str, Any]:
    """
    Update reading log by adding a new entry and committing to GitHub.

    This is the main function browser extensions/mobile apps will call.

    Args:
        owner: Repository owner username
        repo: Repository name
        path: Path to reading.json in repo
        branch: Branch name
        new_entry: New reading entry to add
        access_token: GitHub access token
        commit_message: Optional custom commit message

    Returns:
        Commit response from GitHub

    Raises:
        GitHubAPIError: If update fails
    """
    # Fetch current file
    file_data = await get_file_from_repo(owner, repo, path, branch, access_token)

    # Parse existing content or create new structure
    if file_data["content"]:
        content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
        reading_log = json.loads(content_decoded)
    else:
        reading_log = {"entries": []}

    # Add new entry at the beginning (most recent first)
    reading_log["entries"].insert(0, new_entry)

    # Generate commit message
    if not commit_message:
        entry_title = new_entry.get("title", "article")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Add reading entry: {entry_title} ({timestamp})"

    # Commit updated file
    new_content = json.dumps(reading_log, indent=2, ensure_ascii=False)

    return await commit_file_to_repo(
        owner=owner,
        repo=repo,
        path=path,
        content=new_content,
        message=commit_message,
        branch=branch,
        access_token=access_token,
        sha=file_data["sha"]
    )
