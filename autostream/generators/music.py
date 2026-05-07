"""Music generator — manages music library and generation stubs.

Supports multiple sources:
- Manual import (user drops files into genre folders)
- YouTube Audio Library download (copyright-safe)
- MusicGen (Meta, local, unlimited, open-source)
- Suno/Udio stubs (require browser automation, ToS risk)
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Optional

from autostream.config import LIBRARY_DIR

logger = logging.getLogger(__name__)

DEFAULT_GENRES = ["lofi", "jazz", "ambient"]


def ensure_genre_folders(genres: Optional[list[str]] = None) -> list[Path]:
    """Create genre subfolders under the library directory."""
    genres = genres or DEFAULT_GENRES
    paths = []
    for genre in genres:
        p = LIBRARY_DIR / genre
        p.mkdir(parents=True, exist_ok=True)
        paths.append(p)
    return paths


def list_tracks(genre: str) -> list[dict]:
    """List all audio tracks for a genre."""
    folder = LIBRARY_DIR / genre
    if not folder.exists():
        return []
    exts = (".wav", ".mp3", ".flac", ".ogg", ".aac", ".m4a")
    tracks = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in exts:
            tracks.append({
                "name": f.name,
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                "genre": genre,
            })
    return tracks


def import_track(source_path: str, genre: str) -> str:
    """Import an audio file into the genre library folder."""
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    dest_folder = LIBRARY_DIR / genre
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest = dest_folder / src.name
    shutil.copy2(src, dest)
    logger.info("Imported %s → %s", src.name, dest)
    return str(dest)


def delete_track(genre: str, filename: str) -> bool:
    """Delete a track from the library."""
    path = LIBRARY_DIR / genre / filename
    if path.exists():
        path.unlink()
        logger.info("Deleted %s/%s", genre, filename)
        return True
    return False


def list_genres() -> list[str]:
    """Return all genre folder names."""
    if not LIBRARY_DIR.exists():
        return []
    return sorted(d.name for d in LIBRARY_DIR.iterdir() if d.is_dir())


def get_library_stats() -> dict:
    """Return summary stats for the music library."""
    stats: dict[str, int] = {}
    total = 0
    for genre in list_genres():
        count = len(list_tracks(genre))
        stats[genre] = count
        total += count
    return {"genres": stats, "total_tracks": total}


# ---------- Generation stubs ----------

def generate_musicgen(prompt: str, genre: str, duration_s: int = 30) -> Optional[str]:
    """Stub for MusicGen (Meta) local generation.

    In production, this would:
    1. Load the MusicGen model (facebook/musicgen-small)
    2. Generate audio from prompt
    3. Save to library/<genre>/
    """
    logger.info("MusicGen stub: would generate '%s' for genre=%s, duration=%ds", prompt, genre, duration_s)
    return None


def generate_suno_stub(prompt: str, genre: str) -> Optional[str]:
    """Stub for Suno AI generation (browser automation).

    WARNING: May violate Suno ToS. Use MusicGen for production.
    """
    logger.info("Suno stub: would generate '%s' for genre=%s", prompt, genre)
    return None
