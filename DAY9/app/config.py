"""Application configuration and settings."""

from functools import lru_cache
from pathlib import Path
from typing import Set, Tuple


class Settings:
    """Application settings class."""

    PROJECT_NAME: str = "FastAPI Real-Time Media Hub"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Directories
    BASE_DIR: Path = Path(__file__).resolve().parent
    STATIC_DIR: Path = BASE_DIR / "static"
    UPLOAD_DIR: Path = STATIC_DIR / "uploads"
    ORIGINAL_DIR: Path = UPLOAD_DIR / "original"
    THUMBNAIL_DIR: Path = UPLOAD_DIR / "thumbnail"
    MEDIUM_DIR: Path = UPLOAD_DIR / "medium"

    # Upload validation settings
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "webp", "gif"}
    ALLOWED_MIME_TYPES: Set[str] = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
    }

    # Image resizing dimensions (width, height)
    THUMBNAIL_SIZE: Tuple[int, int] = (150, 150)
    MEDIUM_SIZE: Tuple[int, int] = (600, 600)
    IMAGE_QUALITY: int = 85

    def ensure_directories(self) -> None:
        """Ensure all static upload directories exist."""
        self.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        self.ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
        self.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
        self.MEDIUM_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
