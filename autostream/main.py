"""FastAPI application — YouTube Auto Stream System."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from autostream.db.models import init_db
from autostream.scheduler.jobs import start_scheduler, stop_scheduler
from autostream.generators.music import ensure_genre_folders
from autostream.generators.visual import ensure_theme_folders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard" / "build"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Auto Stream System...")
    init_db()
    ensure_genre_folders()
    ensure_theme_folders()
    start_scheduler()
    logger.info("System ready.")
    yield
    logger.info("Shutting down...")
    stop_scheduler()


app = FastAPI(
    title="YouTube Auto Stream",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
from autostream.api.channels import router as channels_router
from autostream.api.library import router as library_router
from autostream.api.generators import router as generators_router
from autostream.api.logs import router as logs_router
from autostream.api.youtube import router as youtube_router

app.include_router(channels_router)
app.include_router(library_router)
app.include_router(generators_router)
app.include_router(logs_router)
app.include_router(youtube_router)


@app.get("/api/health")
def health():
    from autostream.stream_engine.engine import get_running_channels
    return {
        "status": "ok",
        "streaming_channels": get_running_channels(),
    }


# Serve React dashboard (production build)
if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR / "static"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = DASHBOARD_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DASHBOARD_DIR / "index.html")
