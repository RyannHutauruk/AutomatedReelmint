"""SQLite database models via SQLAlchemy."""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from autostream.config import DB_PATH


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    stream_key = Column(String(255), default="")
    music_folder = Column(String(512), default="library/lofi")
    visual_folder = Column(String(512), default="visuals/aesthetic")
    genre = Column(String(100), default="lofi")
    playback_mode = Column(String(20), default="shuffle")  # shuffle | sequential
    schedule_start = Column(String(10), default="")  # HH:MM or empty for 24/7
    schedule_stop = Column(String(10), default="")
    is_24_7 = Column(Boolean, default=True)
    is_active = Column(Boolean, default=False)
    current_song = Column(String(512), default="")
    current_visual = Column(String(512), default="")
    uptime_seconds = Column(Integer, default=0)
    pid = Column(Integer, default=0)  # ffmpeg process PID
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # OAuth fields
    oauth_client_id = Column(String(512), default="")
    oauth_client_secret = Column(String(512), default="")
    oauth_token_path = Column(String(512), default="")

    titles = relationship("TitleRotation", back_populates="channel", cascade="all, delete-orphan")
    logs = relationship("StreamLog", back_populates="channel", cascade="all, delete-orphan")


class TitleRotation(Base):
    __tablename__ = "title_rotations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    title = Column(String(512), nullable=False)
    sort_order = Column(Integer, default=0)

    channel = relationship("Channel", back_populates="titles")


class StreamLog(Base):
    __tablename__ = "stream_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    level = Column(String(20), default="info")  # info | warning | error
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    channel = relationship("Channel", back_populates="logs")


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gen_type = Column(String(20), nullable=False)  # music | visual
    genre = Column(String(100), default="")
    file_path = Column(String(512), default="")
    status = Column(String(20), default="pending")  # pending | done | failed
    message = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise
