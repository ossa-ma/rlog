"""Reading log CRUD operations router."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth import get_current_user
from models.user import User, GitHubRepo
from models.reading import (
    ReadingEntryCreate,
    ReadingEntry,
    ReadingEntryResponse,
)
from services import github, metadata


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
            print(f"🔍 [/reading/log] Fetching metadata for {entry_data.url}")
            try:
                meta = await metadata.fetch_metadata_safe(str(entry_data.url))
                title = entry_data.title or meta["title"] or str(entry_data.url)
                author = entry_data.author or meta["author"]
                pub_date = entry_data.published_date or meta["publishedDate"]
                print(f"✅ [/reading/log] Metadata fetched: title={title}")
            except Exception as e:
                # If metadata fetch fails, use provided data or fallback
                print(f"⚠️  [/reading/log] Metadata fetch failed: {e}")
                title = entry_data.title or str(entry_data.url)
                author = entry_data.author
                pub_date = entry_data.published_date
        else:
            print(f"⏭️  [/reading/log] Skipping metadata fetch")
            title = entry_data.title or str(entry_data.url)
            author = entry_data.author
            pub_date = entry_data.published_date

        # Create reading entry with today's date in YYYY-MM-DD format
        print(f"📝 [/reading/log] Creating reading entry...")
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
        print(f"✅ [/reading/log] Reading entry created")

        # Commit to GitHub (serialize with camelCase aliases)
        print(f"⬆️  [/reading/log] Committing to GitHub...")
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
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log reading: {str(e)}",
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

        # If it's a flat list (Raycast format), wrap it for API response
        if isinstance(reading_log, list):
            return {"entries": reading_log}

        return reading_log

    except github.GitHubAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading history: {str(e)}",
        )
