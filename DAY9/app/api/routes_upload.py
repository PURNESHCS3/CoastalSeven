"""Image upload and processing API routes."""

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.schemas.upload import ImageItemSummary, ImageListResponse, ImageUploadResponse
from app.services.image_service import ImageService
from app.services.websocket_manager import ConnectionManager, manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["Uploads"])


def get_image_service(
    settings: Settings = Depends(get_settings),
) -> ImageService:
    """Dependency provider for ImageService."""
    return ImageService(settings=settings)


def get_websocket_manager() -> ConnectionManager:
    """Dependency provider for ConnectionManager."""
    return manager


@router.post(
    "",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and resize image",
    description=(
        "Upload an image file (PNG, JPG, WEBP, GIF, up to 5MB). "
        "The server verifies image integrity using Pillow, saves the original, "
        "generates thumbnail (150x150) and medium (600x600) variants, "
        "and broadcasts a real-time notification to all connected WebSocket clients."
    ),
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    image_service: ImageService = Depends(get_image_service),
    ws_manager: ConnectionManager = Depends(get_websocket_manager),
) -> ImageUploadResponse:
    """Upload, validate, resize image and notify WebSocket subscribers."""
    contents = await file.read()

    # Validate file integrity, mime type, size, extension
    image_service.validate_file(
        filename=file.filename,
        content_type=file.content_type,
        file_bytes=contents,
    )

    # Process, resize, and save
    filename = file.filename or "unknown.png"
    content_type = file.content_type or "image/png"
    response = image_service.process_and_save(
        original_filename=filename,
        content_type=content_type,
        file_bytes=contents,
    )

    # Real-time WebSocket notification broadcast
    notification = {
        "event": "IMAGE_UPLOADED",
        "client_id": "system",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": response.model_dump(),
    }
    sent_count = await ws_manager.broadcast(notification)
    logger.info(
        f"Uploaded {response.filename}. Broadcast notification sent to {sent_count} clients."
    )

    return response


@router.get(
    "",
    response_model=ImageListResponse,
    summary="List all uploaded images",
    description="List all stored uploaded images with URLs to original, medium, and thumbnail files.",
)
async def list_images(
    settings: Settings = Depends(get_settings),
) -> ImageListResponse:
    """List all stored uploaded images and their variant URLs."""
    settings.ensure_directories()
    images = []

    if settings.ORIGINAL_DIR.exists():
        for file_path in sorted(settings.ORIGINAL_DIR.glob("*")):
            if file_path.is_file():
                filename = file_path.name
                size = file_path.stat().st_size
                images.append(
                    ImageItemSummary(
                        filename=filename,
                        original_url=f"/static/uploads/original/{filename}",
                        thumbnail_url=f"/static/uploads/thumbnail/{filename}",
                        medium_url=f"/static/uploads/medium/{filename}",
                        size_bytes=size,
                    )
                )

    return ImageListResponse(total_images=len(images), images=images)


@router.get(
    "/{filename}",
    response_model=ImageItemSummary,
    summary="Get uploaded image details",
    description="Fetch URLs and metadata for a specific uploaded image file.",
)
async def get_image_details(
    filename: str,
    settings: Settings = Depends(get_settings),
) -> ImageItemSummary:
    """Get metadata for a specific uploaded image by filename."""
    file_path = settings.ORIGINAL_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{filename}' not found.",
        )

    return ImageItemSummary(
        filename=filename,
        original_url=f"/static/uploads/original/{filename}",
        thumbnail_url=f"/static/uploads/thumbnail/{filename}",
        medium_url=f"/static/uploads/medium/{filename}",
        size_bytes=file_path.stat().st_size,
    )


@router.delete(
    "/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Delete uploaded image and variants",
    description="Removes original, thumbnail, and medium files for the given image filename.",
)
async def delete_image(
    filename: str,
    settings: Settings = Depends(get_settings),
    ws_manager: ConnectionManager = Depends(get_websocket_manager),
) -> dict:
    """Delete an image and its resized variants from disk."""
    original = settings.ORIGINAL_DIR / filename
    thumbnail = settings.THUMBNAIL_DIR / filename
    medium = settings.MEDIUM_DIR / filename

    if not original.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{filename}' not found.",
        )

    for path in (original, thumbnail, medium):
        if path.exists():
            try:
                os.remove(path)
            except OSError:
                pass

    # Broadcast deletion event
    await ws_manager.broadcast(
        {
            "event": "IMAGE_DELETED",
            "client_id": "system",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"filename": filename},
        }
    )

    return {"status": "success", "message": f"Image '{filename}' deleted successfully."}
