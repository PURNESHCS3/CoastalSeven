"""Pytest fixtures and configuration."""

import io
from pathlib import Path
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings, get_settings
from app.main import create_app
from app.services.websocket_manager import manager


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    settings = Settings()
    settings.BASE_DIR = tmp_path
    settings.STATIC_DIR = tmp_path / "static"
    settings.UPLOAD_DIR = settings.STATIC_DIR / "uploads"
    settings.ORIGINAL_DIR = settings.UPLOAD_DIR / "original"
    settings.THUMBNAIL_DIR = settings.UPLOAD_DIR / "thumbnail"
    settings.MEDIUM_DIR = settings.UPLOAD_DIR / "medium"
    settings.ensure_directories()
    return settings


@pytest.fixture
def app_instance(test_settings: Settings) -> Generator[FastAPI, None, None]:
    app = create_app(settings=test_settings)
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app_instance: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app_instance) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_websocket_manager() -> Generator[None, None, None]:
    manager.active_connections.clear()
    yield
    manager.active_connections.clear()


@pytest.fixture
def sample_png_bytes() -> bytes:
    img = Image.new("RGB", (800, 600), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (1000, 800), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_rgba_png_bytes() -> bytes:
    img = Image.new("RGBA", (400, 400), color=(100, 150, 200, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def corrupted_image_bytes() -> bytes:
    return b"This is not a real image header data at all"


@pytest.fixture
def oversize_image_bytes() -> bytes:
    return b"X" * (5 * 1024 * 1024 + 1024)
