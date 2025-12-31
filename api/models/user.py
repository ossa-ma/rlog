from pydantic import BaseModel, Field


class User(BaseModel):
    """User model representing authenticated GitHub user."""

    id: int = Field(..., description="GitHub user ID")
    username: str = Field(..., description="GitHub username")
    email: str | None = Field(None, description="User email from GitHub")
    avatar_url: str | None = Field(None, description="GitHub avatar URL")
    access_token: str = Field(..., description="GitHub access token for API calls")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "username": "ossa-ma",
                "email": "user@example.com",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345",
                "access_token": "gho_xxxxxxxxxxxx",
            }
        }


class UserPublic(BaseModel):
    """Public user information (without sensitive data)."""

    id: int
    username: str
    avatar_url: str | None = None


class GitHubRepo(BaseModel):
    """GitHub repository configuration for user's blog."""

    owner: str = Field(..., description="Repository owner username")
    repo: str = Field(..., description="Repository name")
    branch: str = Field(default="main", description="Branch to commit to")
    reading_json_path: str = Field(
        default="data/reading.json", description="Path to reading.json in repo"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "owner": "ossa-ma",
                "repo": "blog",
                "branch": "main",
                "reading_json_path": "data/reading.json",
            }
        }
