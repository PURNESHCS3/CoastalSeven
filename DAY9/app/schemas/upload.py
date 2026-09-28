"""Upload schemas and models."""

from typing import Dict, List

from pydantic import BaseModel, Field


class ImageVariantInfo(BaseModel):
    """Metadata for an image size variant."""

    url: str = Field(..., description="Static URL to access the variant")
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")
    size_bytes: int = Field(..., description="File size in bytes")


class ImageUploadResponse(BaseModel):
    """Response payload for successful image upload."""

    filename: str = Field(..., description="Generated unique filename on the server")
    original_filename: str = Field(..., description="Original uploaded filename")
    content_type: str = Field(..., description="MIME content type")
    size_bytes: int = Field(..., description="Original image size in bytes")
    width: int = Field(..., description="Original width in pixels")
    height: int = Field(..., description="Original height in pixels")
    url: str = Field(..., description="Static URL to original image")
    variants: Dict[str, ImageVariantInfo] = Field(
        default_factory=dict, description="Processed resized variants"
    )
    uploaded_at: str = Field(..., description="ISO 8601 UTC timestamp of upload")
    message: str = Field(default="Image uploaded and processed successfully")


class ImageItemSummary(BaseModel):
    """Summary information for an uploaded image file."""

    filename: str = Field(..., description="Filename on disk")
    original_url: str = Field(..., description="URL to original image")
    thumbnail_url: str = Field(..., description="URL to 150px thumbnail variant")
    medium_url: str = Field(..., description="URL to 600px medium variant")
    size_bytes: int = Field(..., description="File size of original in bytes")


class ImageListResponse(BaseModel):
    """List of all uploaded images."""

    total_images: int = Field(..., description="Total number of uploaded images")
    images: List[ImageItemSummary] = Field(
        default_factory=list, description="List of image items"
    )
