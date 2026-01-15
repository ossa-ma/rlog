"""GitHub API service for OAuth and repository operations."""

import json
import base64
import ssl
from typing import Any
from datetime import datetime

import aiohttp
import certifi


def _get_ssl_context() -> ssl.SSLContext:
    """Create SSL context using certifi certificates (fixes macOS Python SSL issues)."""
    return ssl.create_default_context(cafile=certifi.where())


def _create_connector() -> aiohttp.TCPConnector:
    """Create TCP connector with proper SSL context."""
    return aiohttp.TCPConnector(ssl=_get_ssl_context())


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
    async with aiohttp.ClientSession(connector=_create_connector()) as session:
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
                    status_code=response.status,
                )

            data = await response.json()

            if "error" in data:
                raise GitHubAPIError(
                    f"GitHub OAuth error: {data.get('error_description', data['error'])}"
                )

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
    async with aiohttp.ClientSession(connector=_create_connector()) as session:
        async with session.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        ) as response:
            if response.status != 200:
                raise GitHubAPIError(
                    f"Failed to fetch user info: {response.status}", status_code=response.status
                )

            return await response.json()


async def get_file_from_repo(
    owner: str, repo: str, path: str, branch: str, access_token: str
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
    async with aiohttp.ClientSession(connector=_create_connector()) as session:
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
                    status_code=response.status,
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
    sha: str | None = None,
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

    async with aiohttp.ClientSession(connector=_create_connector()) as session:
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
                    status_code=response.status,
                )

            return await response.json()


async def update_reading_log(
    owner: str,
    repo: str,
    path: str,
    branch: str,
    new_entry: dict[str, Any],
    access_token: str,
    commit_message: str | None = None,
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Update reading log by adding a new entry and committing to GitHub.
    Handles SHA conflicts by refetching and retrying.

    Args:
        owner: Repository owner username
        repo: Repository name
        path: Path to reading.json in repo
        branch: Branch name
        new_entry: New reading entry to add
        access_token: GitHub access token
        commit_message: Optional custom commit message
        max_retries: Max retries on SHA conflict (default 3)

    Returns:
        Commit response from GitHub

    Raises:
        GitHubAPIError: If update fails after retries
    """
    if not commit_message:
        entry_title = new_entry.get("title", "article")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Add reading entry: {entry_title} ({timestamp})"

    for attempt in range(max_retries):
        file_data = await get_file_from_repo(owner, repo, path, branch, access_token)

        if file_data["content"]:
            content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
            reading_log = json.loads(content_decoded)

            if isinstance(reading_log, dict) and "entries" in reading_log:
                reading_log = reading_log["entries"]
            elif not isinstance(reading_log, list):
                reading_log = []
        else:
            reading_log = []

        # Check for duplicate URL before adding
        new_url = new_entry.get("url")
        if not any(entry.get("url") == new_url for entry in reading_log):
            reading_log.insert(0, new_entry)

        new_content = json.dumps(reading_log, indent=2, ensure_ascii=False)

        try:
            return await commit_file_to_repo(
                owner=owner,
                repo=repo,
                path=path,
                content=new_content,
                message=commit_message,
                branch=branch,
                access_token=access_token,
                sha=file_data["sha"],
            )
        except GitHubAPIError as e:
            if e.status_code == 409 and attempt < max_retries - 1:
                print(f"SHA conflict on attempt {attempt + 1}, retrying...")
                continue
            raise

    raise GitHubAPIError("Failed to update reading log after max retries", status_code=409)


async def delete_reading_entry(
    owner: str,
    repo: str,
    path: str,
    branch: str,
    entry_url: str,
    access_token: str,
    commit_message: str | None = None,
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Delete a reading entry by URL.
    Handles SHA conflicts by refetching and retrying.
    """
    if not commit_message:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Delete reading entry: {entry_url} ({timestamp})"

    for attempt in range(max_retries):
        file_data = await get_file_from_repo(owner, repo, path, branch, access_token)

        if not file_data["content"]:
            # File empty or missing, nothing to delete
            return {"message": "File not found or empty", "sha": None}

        content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
        reading_log = json.loads(content_decoded)

        entries = []
        is_dict_format = False

        if isinstance(reading_log, dict) and "entries" in reading_log:
            entries = reading_log["entries"]
            is_dict_format = True
        elif isinstance(reading_log, list):
            entries = reading_log
            is_dict_format = False
        else:
            # Unknown format, nothing to delete from
            return {"message": "Unknown format", "content": None}

        # Filter out the entry
        original_count = len(entries)
        # Normalize URLs basic stripping for comparison
        target_url = str(entry_url).rstrip("/")
        new_entries = [e for e in entries if str(e.get("url", "")).rstrip("/") != target_url]

        if len(new_entries) == original_count:
            # Nothing deleted, treat as success (idempotent)
            return {"message": "Entry not found", "sha": file_data["sha"]}

        # Reconstruct
        if is_dict_format:
            # reading_log is a dict (likely cast to dict above? No, reading_log is Any/dict from json.loads)
            # We must be careful not to mutate 'reading_log' in a way that breaks type if we didn't cast.
            # reading_log IS a dict here.
            reading_log = dict(reading_log)  # shallow copy safe
            reading_log["entries"] = new_entries
            new_content_obj = reading_log
        else:
            new_content_obj = new_entries

        new_content = json.dumps(new_content_obj, indent=2, ensure_ascii=False)

        try:
            return await commit_file_to_repo(
                owner=owner,
                repo=repo,
                path=path,
                content=new_content,
                message=commit_message,
                branch=branch,
                access_token=access_token,
                sha=file_data["sha"],
            )
        except GitHubAPIError as e:
            if e.status_code == 409 and attempt < max_retries - 1:
                # print(f"SHA conflict on attempt {attempt + 1}, retrying...")
                continue
            raise

    raise GitHubAPIError("Failed to delete entry after max retries", status_code=409)
