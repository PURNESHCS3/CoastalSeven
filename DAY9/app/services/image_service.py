"""Service for validating, processing, and resizing images with Pillow."""

import io
import os
import uuid
from datetime import datetime, timezone
from typing import Dict

from PIL import Image, UnidentifiedImageError

from app.config import Settings, get_settings
from app.core.exceptions import (
    FileTooLargeError,
    ImageProcessingError,
    ImageValidationError,
    UnsupportedMediaTypeError,
)
from app.schemas.upload import ImageUploadResponse, ImageVariantInfo


class ImageService:
    """Service handling image validation and resizing operations."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def validate_file(
        self,
        filename: str | None,
        content_type: str | None,
        file_bytes: bytes,
    ) -> None:
        """Validate file size, extension, MIME type, and Pillow integrity."""
        # 1. Check size limit
        if len(file_bytes) > self.settings.MAX_FILE_SIZE_BYTES:
            max_mb = self.settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise FileTooLargeError(max_size_mb=max_mb)

        if not filename or "." not in filename:
            raise UnsupportedMediaTypeError("Missing or invalid file extension.")

        # 2. Check file extension
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in self.settings.ALLOWED_EXTENSIONS:
            raise UnsupportedMediaTypeError(
                f"Extension '.{ext}' is not supported. "
                f"Allowed: {', '.join(sorted(self.settings.ALLOWED_EXTENSIONS))}"
            )

        # 3. Check MIME content type
        if content_type not in self.settings.ALLOWED_MIME_TYPES:
            raise UnsupportedMediaTypeError(
                f"Content type '{content_type}' is not supported."
            )

        # 4. Verify image content with Pillow to detect spoofed/corrupted files
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()
        except (UnidentifiedImageError, OSError, Exception) as exc:
            raise ImageValidationError(
                f"Uploaded file failed image verification: {exc}"
            )

    def _prepare_image_for_save(
        self, img: Image.Image, output_format: str
    ) -> Image.Image:
        """Convert image mode if necessary for the target output format."""
        if output_format.upper() in ("JPEG", "JPG"):
            if img.mode in ("RGBA", "LA", "P"):
                # Create white background for transparent images converted to JPEG
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                return background
            elif img.mode != "RGB":
                return img.convert("RGB")
        return img

    def process_and_save(
        self,
        original_filename: str,
        content_type: str,
        file_bytes: bytes,
    ) -> ImageUploadResponse:
        """Save original image and create thumbnail and medium resized versions."""
        self.settings.ensure_directories()

        ext = original_filename.rsplit(".", 1)[-1].lower()
        unique_id = uuid.uuid4().hex
        saved_filename = f"{unique_id}.{ext}"

        # 1. Save original image
        original_path = self.settings.ORIGINAL_DIR / saved_filename
        try:
            with open(original_path, "wb") as f:
                f.write(file_bytes)
        except OSError as exc:
            raise ImageProcessingError(f"Failed to save original file: {exc}")

        # 2. Open and inspect dimensions
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                orig_width, orig_height = img.size
                img_format = img.format or ext.upper()

                variants: Dict[str, ImageVariantInfo] = {}

                # Create Thumbnail
                thumb_img = img.copy()
                thumb_img.thumbnail(
                    self.settings.THUMBNAIL_SIZE, Image.Resampling.LANCZOS
                )
                thumb_img = self._prepare_image_for_save(thumb_img, img_format)
                thumb_path = self.settings.THUMBNAIL_DIR / saved_filename
                thumb_img.save(
                    thumb_path,
                    format=img_format,
                    quality=self.settings.IMAGE_QUALITY,
                )
                thumb_size = os.path.getsize(thumb_path)
                variants["thumbnail"] = ImageVariantInfo(
                    url=f"/static/uploads/thumbnail/{saved_filename}",
                    width=thumb_img.width,
                    height=thumb_img.height,
                    size_bytes=thumb_size,
                )

                # Create Medium size
                medium_img = img.copy()
                medium_img.thumbnail(
                    self.settings.MEDIUM_SIZE, Image.Resampling.LANCZOS
                )
                medium_img = self._prepare_image_for_save(medium_img, img_format)
                medium_path = self.settings.MEDIUM_DIR / saved_filename
                medium_img.save(
                    medium_path,
                    format=img_format,
                    quality=self.settings.IMAGE_QUALITY,
                )
                medium_size = os.path.getsize(medium_path)
                variants["medium"] = ImageVariantInfo(
                    url=f"/static/uploads/medium/{saved_filename}",
                    width=medium_img.width,
                    height=medium_img.height,
                    size_bytes=medium_size,
                )

        except Exception as exc:
            # Clean up original file if processing fails
            if original_path.exists():
                original_path.unlink(missing_ok=True)
            raise ImageProcessingError(f"Failed to resize image: {exc}")

        return ImageUploadResponse(
            filename=saved_filename,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=len(file_bytes),
            width=orig_width,
            height=orig_height,
            url=f"/static/uploads/original/{saved_filename}",
            variants=variants,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            message="Image uploaded and resized successfully",
        )
