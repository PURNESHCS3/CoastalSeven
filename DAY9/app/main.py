"""FastAPI Real-Time Media Application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_upload import router as upload_router
from app.api.routes_views import router as views_router
from app.api.routes_websocket import router as websocket_router
from app.config import Settings, get_settings
from app.services.websocket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for application startup and shutdown."""
    settings = get_settings()
    # 1. Startup: ensure static & upload directories exist
    settings.ensure_directories()
    yield
    # 2. Shutdown: safely close active WebSocket connections
    await manager.close_all()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.PROJECT_NAME,
        version=app_settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files mounting
    app_settings.ensure_directories()
    app.mount("/static", StaticFiles(directory=app_settings.STATIC_DIR), name="static")

    # Include API and View routers
    app.include_router(views_router)
    app.include_router(upload_router)
    app.include_router(websocket_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
