from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class BaseReadingEntry(BaseModel):
    """Base reading entry with common fields."""

    url: HttpUrl = Field(..., description="URL of the article/content")
    title: str | None = Field(None, description="Article title")
    author: str | None = Field(None, description="Article author")
    publication_date: str | None = Field(None, description="Publication date")
    comment: str | None = Field(None, description="User comment about the reading")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class ReadingEntryCreate(BaseReadingEntry):
    """Request model for creating a new reading entry."""

    fetch_metadata: bool = Field(
        default=True, description="Whether to automatically fetch title/author/date"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/article",
                "comment": "Great insights on async Python",
                "tags": ["python", "async"],
                "fetch_metadata": True,
            }
        }
    )


class ReadingEntry(BaseReadingEntry):
    """Complete reading entry as stored in reading.json."""

    date_read: datetime = Field(
        default_factory=datetime.now, description="Timestamp when article was logged"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/article",
                "title": "Understanding Async Python",
                "author": "John Doe",
                "publication_date": "2024-01-15",
                "date_read": "2024-01-20T10:30:00",
                "comment": "Great insights on async Python",
                "tags": ["python", "async"],
            }
        }
    )


class ReadingLog(BaseModel):
    """Complete reading log (reading.json structure)."""

    entries: list[ReadingEntry] = Field(default_factory=list, description="List of reading entries")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entries": [
                    {
                        "url": "https://example.com/article1",
                        "title": "Article 1",
                        "date_read": "2024-01-20T10:30:00",
                    }
                ]
            }
        }
    )


class ReadingEntryResponse(BaseModel):
    """API response after creating/updating an entry."""

    success: bool
    entry: ReadingEntry
    message: str = "Entry logged successfully"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "entry": {
                    "url": "https://example.com/article",
                    "title": "Understanding Async Python",
                    "date_read": "2024-01-20T10:30:00",
                },
                "message": "Entry logged successfully",
            }
        }
    )
