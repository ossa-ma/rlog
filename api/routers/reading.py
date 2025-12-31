"""Reading log CRUD operations router."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from api.middleware.auth import get_current_user
from api.models.user import User, GitHubRepo
from api.models.reading import (
    ReadingEntryCreate,
    ReadingEntry,
    ReadingEntryResponse,
    CommitRequest,
)
from api.services import github, metadata


router = APIRouter(prefix="/reading", tags=["reading"])


@router.post("/log", response_model=ReadingEntryResponse)
async def log_reading(
    entry_data: ReadingEntryCreate,
    repo_config: GitHubRepo,
    current_user: User = Depends(get_current_user),
) -> ReadingEntryResponse:
    """
    Log a new reading entry and commit to user's GitHub repository.

    This is the main endpoint browser extensions and mobile apps will use.

    Workflow:
    1. Optionally fetch metadata (title, author, date) from URL
    2. Create reading entry with timestamp
    3. Fetch current reading.json from user's repo
    4. Add new entry to the log
    5. Commit updated reading.json back to repo

    Args:
        entry_data: Reading entry information (URL, comment, tags)
        repo_config: GitHub repository configuration
        current_user: Authenticated user (from JWT)

    Returns:
        Success response with created entry

    Raises:
        HTTPException: If logging fails
    """
    try:
        # Fetch metadata if requested
        if entry_data.fetch_metadata:
            try:
                meta = await metadata.fetch_metadata_safe(str(entry_data.url))
                title = entry_data.title or meta["title"]
                author = entry_data.author or meta["author"]
                pub_date = entry_data.publication_date or meta["publication_date"]
            except Exception:
                # If metadata fetch fails, use provided data or None
                title = entry_data.title
                author = entry_data.author
                pub_date = entry_data.publication_date
        else:
            title = entry_data.title
            author = entry_data.author
            pub_date = entry_data.publication_date

        # Create reading entry
        reading_entry = ReadingEntry(
            url=entry_data.url,
            title=title,
            author=author,
            publication_date=pub_date,
            date_read=datetime.now(),
            comment=entry_data.comment,
            tags=entry_data.tags,
        )

        # Commit to GitHub
        await github.update_reading_log(
            owner=repo_config.owner,
            repo=repo_config.repo,
            path=repo_config.reading_json_path,
            branch=repo_config.branch,
            new_entry=reading_entry.model_dump(mode="json"),
            access_token=current_user.access_token,
        )

        return ReadingEntryResponse(
            success=True,
            entry=reading_entry,
            message="Reading entry logged successfully",
        )

    except github.GitHubAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log reading: {str(e)}"
        )


@router.post("/commit", response_model=dict)
async def commit_reading_log(
    commit_data: CommitRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Manually trigger commit of local reading log to GitHub.

    This endpoint is for advanced users who manage reading.json locally
    and want to push it to GitHub via API.

    Args:
        commit_data: Commit configuration
        current_user: Authenticated user (from JWT)

    Returns:
        Success response with commit details

    Raises:
        HTTPException: If commit fails
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Manual commit endpoint not yet implemented. Use /log to add entries."
    )


@router.get("/history", response_model=dict)
async def get_reading_history(
    repo_owner: str,
    repo_name: str,
    branch: str = "main",
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Fetch user's reading history from their GitHub repository.

    Args:
        repo_owner: Repository owner username
        repo_name: Repository name
        branch: Branch name (default: main)
        current_user: Authenticated user (from JWT)

    Returns:
        Reading log data

    Raises:
        HTTPException: If fetch fails
    """
    try:
        file_data = await github.get_file_from_repo(
            owner=repo_owner,
            repo=repo_name,
            path="data/reading.json",
            branch=branch,
            access_token=current_user.access_token,
        )

        if not file_data["content"]:
            return {"entries": []}

        import base64
        import json

        content = base64.b64decode(file_data["content"]).decode("utf-8")
        reading_log = json.loads(content)

        return reading_log

    except github.GitHubAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {str(e)}"
        )
