"""Library management API — music tracks & visual files."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path

from autostream.config import LIBRARY_DIR, VISUALS_DIR
from autostream.generators.music import (
    delete_track,
    get_library_stats,
    list_genres,
    list_tracks,
)
from autostream.generators.visual import (
    delete_visual,
    get_visuals_stats,
    list_themes,
    list_visuals,
)

router = APIRouter(prefix="/api/library", tags=["library"])


# ── Music ────────────────────────────────────────────────────────────

@router.get("/music/stats")
def music_stats():
    return get_library_stats()


@router.get("/music/genres")
def music_genres():
    return list_genres()


@router.get("/music/{genre}")
def music_tracks(genre: str):
    return list_tracks(genre)


@router.post("/music/{genre}/upload")
async def upload_music(genre: str, file: UploadFile = File(...)):
    dest_folder = LIBRARY_DIR / genre
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest = dest_folder / file.filename
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"detail": "Uploaded", "path": str(dest), "genre": genre}


@router.delete("/music/{genre}/{filename}")
def remove_music(genre: str, filename: str):
    if not delete_track(genre, filename):
        raise HTTPException(status_code=404, detail="Track not found")
    return {"detail": "Deleted"}


# ── Visuals ──────────────────────────────────────────────────────────

@router.get("/visuals/stats")
def visuals_stats():
    return get_visuals_stats()


@router.get("/visuals/themes")
def visual_themes():
    return list_themes()


@router.get("/visuals/{theme}")
def visual_files(theme: str):
    return list_visuals(theme)


@router.post("/visuals/{theme}/upload")
async def upload_visual(theme: str, file: UploadFile = File(...)):
    dest_folder = VISUALS_DIR / theme
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest = dest_folder / file.filename
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"detail": "Uploaded", "path": str(dest), "theme": theme}


@router.delete("/visuals/{theme}/{filename}")
def remove_visual(theme: str, filename: str):
    if not delete_visual(theme, filename):
        raise HTTPException(status_code=404, detail="Visual not found")
    return {"detail": "Deleted"}
