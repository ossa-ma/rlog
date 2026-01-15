"""Reading log CRUD operations router."""

from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth import get_current_user
from models.user import User, GitHubRepo
from models.reading import (
    ReadingEntryCreate,
    ReadingEntry,
    ReadingEntryResponse,
    DeleteEntryData,
)
from services import github, metadata

log = logging.getLogger(__name__)


router = APIRouter(prefix="/reading", tags=["reading"])


@router.post("/log", response_model=ReadingEntryResponse)
async def log_reading(
    entry_data: ReadingEntryCreate,
    repo_config: GitHubRepo,
    current_user: User = Depends(get_current_user),
) -> ReadingEntryResponse:
    """Log a new reading entry and commit to user's GitHub repository.

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
            log.info(f"Fetching metadata for {entry_data.url}")
            try:
                meta = await metadata.fetch_metadata_safe(str(entry_data.url))
                title = entry_data.title or meta["title"] or str(entry_data.url)
                author = entry_data.author or meta["author"]
                pub_date = entry_data.published_date or meta["publishedDate"]
                log.info(f"Metadata fetched: title={title}")
            except Exception as e:
                # If metadata fetch fails, use provided data or fallback
                log.warning(f"Metadata fetch failed: {e}")
                title = entry_data.title or str(entry_data.url)
                author = entry_data.author
                pub_date = entry_data.published_date
        else:
            log.info("Skipping metadata fetch")
            title = entry_data.title or str(entry_data.url)
            author = entry_data.author
            pub_date = entry_data.published_date

        # Create reading entry with today's date in YYYY-MM-DD format
        log.info("Creating reading entry...")
        today = datetime.now().strftime("%Y-%m-%d")

        reading_entry = ReadingEntry(
            url=entry_data.url,
            title=title,
            author=author,
            published_date=pub_date,
            added_date=today,
            thoughts=entry_data.thoughts,
            rating=entry_data.rating,
        )
        log.info("Reading entry created")

        # Commit to GitHub (serialize with camelCase aliases)
        log.info("Committing to GitHub...")
        entry_dict = reading_entry.model_dump(by_alias=True, exclude_none=True, mode="json")

        await github.update_reading_log(
            owner=repo_config.owner,
            repo=repo_config.repo,
            path=repo_config.reading_json_path,
            branch=repo_config.branch,
            new_entry=entry_dict,
            access_token=current_user.access_token,
        )

        return ReadingEntryResponse(
            success=True,
            entry=reading_entry,
            message="Reading entry logged successfully",
        )

    except github.GitHubAPIError as e:
        log.error(f"GitHub API error: {e.message}")
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {e.message}",
        )
    except Exception as e:
        log.error(f"Failed to log reading: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log reading: {str(e)}",
        )


@router.get("/history", response_model=dict)
async def get_reading_history(
    repo_owner: str,
    repo_name: str,
    branch: str = "main",
    file_path: str = "data/reading.json",
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Fetch user's reading history or list from their GitHub repository.

    Args:
        repo_owner: Repository owner username
        repo_name: Repository name
        branch: Branch name (default: main)
        file_path: Path to JSON file (default: data/reading.json)
        current_user: Authenticated user (from JWT)

    Returns:
        Reading log data

    Raises:
        HTTPException: If fetch fails
    """
    try:
        log.info(f"Fetching history from {repo_owner}/{repo_name}/{file_path}")
        file_data = await github.get_file_from_repo(
            owner=repo_owner,
            repo=repo_name,
            path=file_path,
            branch=branch,
            access_token=current_user.access_token,
        )

        if not file_data["content"]:
            log.warning("File content empty")
            return {"entries": []}

        import base64
        import json

        content = base64.b64decode(file_data["content"]).decode("utf-8")
        reading_log = json.loads(content)

        # If it's a flat list (Raycast format), wrap it for API response
        if isinstance(reading_log, list):
            log.info(f"Fetched {len(reading_log)} entries")
            return {"entries": reading_log}

        log.info(f"Fetched data (structure: {type(reading_log)})")
        return reading_log

    except github.GitHubAPIError as e:
        log.error(f"GitHub API error fetching history: {e.message}")
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {e.message}",
        )
    except Exception as e:
        log.error(f"Failed to fetch reading history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {str(e)}",
        )


@router.delete("/log", response_model=dict)
async def delete_log_entry(
    entry_data: DeleteEntryData,
    repo_config: GitHubRepo,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete an entry from the reading log."""
    try:
        log.info(f"Deleting log entry: {entry_data.url}")
        result = await github.delete_reading_entry(
            owner=repo_config.owner,
            repo=repo_config.repo,
            path=repo_config.reading_json_path,
            branch=repo_config.branch,
            entry_url=str(entry_data.url),
            access_token=current_user.access_token,
        )
        return {"success": True, "message": "Entry deleted successfully", "github_response": result}

    except github.GitHubAPIError as e:
        log.error(f"GitHub API error: {e.message}")
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {e.message}",
        )
    except Exception as e:
        log.error(f"Failed to delete entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entry: {str(e)}",
        )


@router.delete("/list", response_model=dict)
async def delete_read_later_entry(
    entry_data: DeleteEntryData,
    repo_config: GitHubRepo,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete an entry from the reading list (read later)."""
    try:
        log.info(f"Deleting read later entry: {entry_data.url}")
        result = await github.delete_reading_entry(
            owner=repo_config.owner,
            repo=repo_config.repo,
            path=repo_config.reading_json_path,  # Client must provide correct path for list
            branch=repo_config.branch,
            entry_url=str(entry_data.url),
            access_token=current_user.access_token,
        )
        return {"success": True, "message": "Entry deleted successfully", "github_response": result}

    except github.GitHubAPIError as e:
        log.error(f"GitHub API error: {e.message}")
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {e.message}",
        )
    except Exception as e:
        log.error(f"Failed to delete entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entry: {str(e)}",
        )
