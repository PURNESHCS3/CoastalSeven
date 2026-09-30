"""General API routes: Root redirect to Swagger and Health check."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import get_settings

router = APIRouter(tags=["General"])


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root path to interactive Swagger UI documentation."""
    return RedirectResponse(url="/docs")


@router.get(
    "/health",
    summary="Health check",
    description="Check the operational status of the service.",
    response_class=JSONResponse,
)
async def health_check() -> JSONResponse:
    """Return health status of the application."""
    settings = get_settings()
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
        }
    )
