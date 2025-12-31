from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Server
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # GitHub OAuth
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # Optional: Future Pro features
    openai_api_key: str | None = None
    database_url: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


# Global settings instance
settings = Settings()
