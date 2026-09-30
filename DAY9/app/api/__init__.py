"""API routes package."""

from app.api.routes_upload import router as upload_router
from app.api.routes_views import router as views_router
from app.api.routes_websocket import router as websocket_router

__all__ = ["upload_router", "websocket_router", "views_router"]
