"""Logs API — per-channel stream logs and generation history."""

from __future__ import annotations

from fastapi import APIRouter, Query

from autostream.db.models import GenerationLog, SessionLocal, StreamLog

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/stream")
def stream_logs(channel_id: int = Query(None), limit: int = 100):
    db = SessionLocal()
    try:
        q = db.query(StreamLog).order_by(StreamLog.timestamp.desc())
        if channel_id is not None:
            q = q.filter(StreamLog.channel_id == channel_id)
        rows = q.limit(limit).all()
        return [
            {
                "id": r.id,
                "channel_id": r.channel_id,
                "level": r.level,
                "message": r.message,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in rows
        ]
    finally:
        db.close()


@router.get("/generation")
def generation_logs(gen_type: str = Query(None), limit: int = 100):
    db = SessionLocal()
    try:
        q = db.query(GenerationLog).order_by(GenerationLog.timestamp.desc())
        if gen_type:
            q = q.filter(GenerationLog.gen_type == gen_type)
        rows = q.limit(limit).all()
        return [
            {
                "id": r.id,
                "gen_type": r.gen_type,
                "genre": r.genre,
                "file_path": r.file_path,
                "status": r.status,
                "message": r.message,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in rows
        ]
    finally:
        db.close()
