from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_serializer


class ReadingEntryCreate(BaseModel):
    """Request model for creating a new reading entry (matches Raycast)."""

    url: HttpUrl = Field(..., description="URL of the article/content")
    title: str | None = Field(None, description="Article title")
    author: str | None = Field(None, description="Article author")
    published_date: str | None = Field(
        None, description="Publication date (YYYY-MM-DD)", serialization_alias="publishedDate"
    )
    thoughts: str | None = Field(None, description="User thoughts/notes")
    rating: int | None = Field(None, ge=1, le=5, description="Optional 1-5 rating")
    fetch_metadata: bool = Field(
        default=True, description="Auto-fetch metadata", serialization_alias="fetchMetadata"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "url": "https://example.com/article",
                "thoughts": "Great insights",
                "rating": 4,
                "fetchMetadata": True,
            }
        },
    )


class ReadingEntry(BaseModel):
    """Complete reading entry as stored in reading.json (matches Raycast exactly)."""

    url: HttpUrl = Field(..., description="URL of the article/content")
    title: str = Field(..., description="Article title")
    author: str | None = Field(None, description="Article author (null if unknown)")
    published_date: str | None = Field(
        None, description="Publication date YYYY-MM-DD", serialization_alias="publishedDate"
    )
    added_date: str = Field(
        ..., description="Date logged YYYY-MM-DD", serialization_alias="addedDate"
    )
    thoughts: str | None = Field(None, description="User thoughts/notes")
    rating: int | None = Field(None, ge=1, le=5, description="Optional 1-5 rating")

    @field_serializer("url")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "url": "https://example.com/article",
                "title": "Understanding Async Python",
                "author": "John Doe",
                "publishedDate": "2024-01-15",
                "addedDate": "2024-01-20",
                "thoughts": "Great insights",
                "rating": 4,
            }
        },
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
                    "addedDate": "2024-01-20",
                },
                "message": "Entry logged successfully",
            }
        }
    )


class DeleteEntryData(BaseModel):
    """Data for identifying entry to delete."""

    url: HttpUrl = Field(..., description="URL of the entry to delete")

    model_config = ConfigDict(json_schema_extra={"example": {"url": "https://example.com/article"}})
