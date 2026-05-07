"""Channel management API routes."""

from __future__ import annotations

import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from autostream.db.models import Channel, SessionLocal, StreamLog, TitleRotation
from autostream.stream_engine.engine import is_streaming, start_stream, stop_stream

router = APIRouter(prefix="/api/channels", tags=["channels"])


class ChannelCreate(BaseModel):
    name: str
    stream_key: str = ""
    music_folder: str = "library/lofi"
    visual_folder: str = "visuals/aesthetic"
    genre: str = "lofi"
    playback_mode: str = "shuffle"
    schedule_start: str = ""
    schedule_stop: str = ""
    is_24_7: bool = True
    titles: list[str] = []
    oauth_client_id: str = ""
    oauth_client_secret: str = ""


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    stream_key: Optional[str] = None
    music_folder: Optional[str] = None
    visual_folder: Optional[str] = None
    genre: Optional[str] = None
    playback_mode: Optional[str] = None
    schedule_start: Optional[str] = None
    schedule_stop: Optional[str] = None
    is_24_7: Optional[bool] = None
    titles: Optional[list[str]] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None


def _channel_to_dict(ch: Channel) -> dict:
    return {
        "id": ch.id,
        "name": ch.name,
        "stream_key": ch.stream_key,
        "music_folder": ch.music_folder,
        "visual_folder": ch.visual_folder,
        "genre": ch.genre,
        "playback_mode": ch.playback_mode,
        "schedule_start": ch.schedule_start,
        "schedule_stop": ch.schedule_stop,
        "is_24_7": ch.is_24_7,
        "is_active": is_streaming(ch.id),
        "current_song": ch.current_song,
        "current_visual": ch.current_visual,
        "uptime_seconds": ch.uptime_seconds,
        "titles": [t.title for t in ch.titles],
        "created_at": ch.created_at.isoformat() if ch.created_at else None,
    }


@router.get("")
def list_channels():
    db = SessionLocal()
    try:
        channels = db.query(Channel).all()
        return [_channel_to_dict(ch) for ch in channels]
    finally:
        db.close()


@router.post("")
def create_channel(data: ChannelCreate):
    db = SessionLocal()
    try:
        ch = Channel(
            name=data.name,
            stream_key=data.stream_key,
            music_folder=data.music_folder,
            visual_folder=data.visual_folder,
            genre=data.genre,
            playback_mode=data.playback_mode,
            schedule_start=data.schedule_start,
            schedule_stop=data.schedule_stop,
            is_24_7=data.is_24_7,
            oauth_client_id=data.oauth_client_id,
            oauth_client_secret=data.oauth_client_secret,
        )
        db.add(ch)
        db.flush()

        for i, title in enumerate(data.titles):
            db.add(TitleRotation(channel_id=ch.id, title=title, sort_order=i))

        db.commit()
        db.refresh(ch)
        return _channel_to_dict(ch)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.get("/{channel_id}")
def get_channel(channel_id: int):
    db = SessionLocal()
    try:
        ch = db.query(Channel).filter(Channel.id == channel_id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")
        return _channel_to_dict(ch)
    finally:
        db.close()


@router.put("/{channel_id}")
def update_channel(channel_id: int, data: ChannelUpdate):
    db = SessionLocal()
    try:
        ch = db.query(Channel).filter(Channel.id == channel_id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")

        update_data = data.model_dump(exclude_unset=True)
        titles_list = update_data.pop("titles", None)

        for key, value in update_data.items():
            setattr(ch, key, value)

        if titles_list is not None:
            db.query(TitleRotation).filter(TitleRotation.channel_id == channel_id).delete()
            for i, title in enumerate(titles_list):
                db.add(TitleRotation(channel_id=channel_id, title=title, sort_order=i))

        ch.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(ch)
        return _channel_to_dict(ch)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.delete("/{channel_id}")
def delete_channel(channel_id: int):
    db = SessionLocal()
    try:
        ch = db.query(Channel).filter(Channel.id == channel_id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")

        if is_streaming(channel_id):
            stop_stream(channel_id)

        db.delete(ch)
        db.commit()
        return {"detail": "Channel deleted"}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/{channel_id}/start")
def start_channel_stream(channel_id: int):
    db = SessionLocal()
    try:
        ch = db.query(Channel).filter(Channel.id == channel_id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")
        if not ch.stream_key:
            raise HTTPException(status_code=400, detail="No stream key configured")

        def on_song_change(cid: int, song: str, visual: str):
            s = SessionLocal()
            try:
                c = s.query(Channel).filter(Channel.id == cid).first()
                if c:
                    c.current_song = song
                    c.current_visual = visual
                    s.commit()
            finally:
                s.close()

        ok = start_stream(
            channel_id, ch.music_folder, ch.visual_folder,
            ch.stream_key, ch.playback_mode, on_song_change,
        )
        if not ok:
            raise HTTPException(status_code=409, detail="Channel already streaming")

        ch.is_active = True
        db.add(StreamLog(channel_id=channel_id, level="info", message="Stream started manually"))
        db.commit()
        return {"detail": "Stream started"}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/{channel_id}/stop")
def stop_channel_stream(channel_id: int):
    db = SessionLocal()
    try:
        ch = db.query(Channel).filter(Channel.id == channel_id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")

        stop_stream(channel_id)
        ch.is_active = False
        ch.current_song = ""
        ch.current_visual = ""
        db.add(StreamLog(channel_id=channel_id, level="info", message="Stream stopped manually"))
        db.commit()
        return {"detail": "Stream stopped"}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
