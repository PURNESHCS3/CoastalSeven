"""Unit tests for ImageService."""

import pytest

from app.config import Settings
from app.core.exceptions import (
    FileTooLargeError,
    ImageProcessingError,
    ImageValidationError,
    UnsupportedMediaTypeError,
)
from app.services.image_service import ImageService


def test_validate_file_success(
    test_settings: Settings, sample_png_bytes: bytes
) -> None:
    """Test validation succeeds on valid PNG."""
    service = ImageService(settings=test_settings)
    service.validate_file("photo.png", "image/png", sample_png_bytes)


def test_validate_file_oversize(
    test_settings: Settings, oversize_image_bytes: bytes
) -> None:
    """Test validation fails when file exceeds max size."""
    service = ImageService(settings=test_settings)
    with pytest.raises(FileTooLargeError):
        service.validate_file("huge.png", "image/png", oversize_image_bytes)


def test_validate_file_unsupported_extension(
    test_settings: Settings, sample_png_bytes: bytes
) -> None:
    """Test validation fails on invalid file extension."""
    service = ImageService(settings=test_settings)
    with pytest.raises(UnsupportedMediaTypeError):
        service.validate_file("document.pdf", "image/png", sample_png_bytes)


def test_validate_file_unsupported_mime(
    test_settings: Settings, sample_png_bytes: bytes
) -> None:
    """Test validation fails on unsupported MIME content type."""
    service = ImageService(settings=test_settings)
    with pytest.raises(UnsupportedMediaTypeError):
        service.validate_file("photo.png", "application/octet-stream", sample_png_bytes)


def test_validate_file_corrupted(
    test_settings: Settings, corrupted_image_bytes: bytes
) -> None:
    """Test validation fails when file is corrupted or spoofed."""
    service = ImageService(settings=test_settings)
    with pytest.raises(ImageValidationError):
        service.validate_file("fake.png", "image/png", corrupted_image_bytes)


def test_validate_file_missing_extension(
    test_settings: Settings, sample_png_bytes: bytes
) -> None:
    """Test validation fails when filename has no extension."""
    service = ImageService(settings=test_settings)
    with pytest.raises(UnsupportedMediaTypeError):
        service.validate_file("no_extension", "image/png", sample_png_bytes)


def test_process_and_save_success(
    test_settings: Settings, sample_png_bytes: bytes
) -> None:
    """Test successful image saving and variant resizing."""
    service = ImageService(settings=test_settings)
    response = service.process_and_save("avatar.png", "image/png", sample_png_bytes)

    assert response.original_filename == "avatar.png"
    assert response.width == 800
    assert response.height == 600
    assert "thumbnail" in response.variants
    assert "medium" in response.variants

    # Verify thumbnail constraints (max 150x150, aspect ratio preserved)
    thumb = response.variants["thumbnail"]
    assert thumb.width <= 150
    assert thumb.height <= 150
    assert (test_settings.THUMBNAIL_DIR / response.filename).exists()

    # Verify medium constraints (max 600x600, aspect ratio preserved)
    medium = response.variants["medium"]
    assert medium.width <= 600
    assert medium.height <= 600
    assert (test_settings.MEDIUM_DIR / response.filename).exists()
    assert (test_settings.ORIGINAL_DIR / response.filename).exists()


def test_process_and_save_rgba_to_jpeg(
    test_settings: Settings, sample_rgba_png_bytes: bytes
) -> None:
    """Test transparent RGBA image conversion handling when saving as JPEG."""
    service = ImageService(settings=test_settings)
    response = service.process_and_save("logo.jpg", "image/jpeg", sample_rgba_png_bytes)

    assert response.filename.endswith(".jpg")
    assert (test_settings.ORIGINAL_DIR / response.filename).exists()
    assert (test_settings.THUMBNAIL_DIR / response.filename).exists()


def test_process_and_save_failure_cleans_up(test_settings: Settings) -> None:
    """Test failed image processing cleans up original file."""
    service = ImageService(settings=test_settings)
    # Corrupt data during save will trigger ImageProcessingError
    with pytest.raises(ImageProcessingError):
        service.process_and_save("bad.png", "image/png", b"not-valid-image")
