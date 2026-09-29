from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# Settings
# ============================================================

class Settings(BaseSettings):

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_REFRESH_SECRET: str = "day10_refresh_super_secret_key"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"

    CELERY_RESULT_BACKEND: str = (
        "redis://localhost:6379/2"
    )

    # ========================================================
    # SMTP / EMAIL SETTINGS
    # ========================================================

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()


# ============================================================
# PostgreSQL Engine
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# Database Session
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# SQLAlchemy Base
# ============================================================

Base = declarative_base()


# ============================================================
# Database Dependency
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()