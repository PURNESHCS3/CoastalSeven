"""Custom application exceptions."""

from fastapi import HTTPException, status


class MediaHubException(HTTPException):
    """Base exception for Media Hub application."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


class FileTooLargeError(MediaHubException):
    """Exception raised when uploaded file exceeds allowed size."""

    def __init__(self, max_size_mb: float) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {max_size_mb:.1f} MB.",
        )


class UnsupportedMediaTypeError(MediaHubException):
    """Exception raised when uploaded file has an unsupported format or mime type."""

    def __init__(self, detail: str = "Unsupported image media type.") -> None:
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=detail,
        )


class ImageValidationError(MediaHubException):
    """Exception raised when uploaded image fails integrity check."""

    def __init__(self, detail: str = "Invalid or corrupted image file.") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ImageProcessingError(MediaHubException):
    """Exception raised when image transformation fails."""

    def __init__(self, detail: str = "Error occurred while processing image.") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
