"""
Centralized application configuration.
Reads from a .env file (see .env.example) so secrets never live in source code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = "dev-only-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Database
    DATABASE_URL: str = "sqlite:///./ats_system.db"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_SIZE_MB: int = 5

    # Default admin seed
    ADMIN_EMAIL: str = "admin@octosafes-ats.com"
    ADMIN_PASSWORD: str = "Admin@12345"
    ADMIN_NAME: str = "System Admin"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def resume_dir(self) -> str:
        return f"{self.UPLOAD_DIR}/resumes"

    @property
    def profile_picture_dir(self) -> str:
        return f"{self.UPLOAD_DIR}/profile_pictures"


settings = Settings()
