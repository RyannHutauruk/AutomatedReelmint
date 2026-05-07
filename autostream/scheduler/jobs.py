"""APScheduler-based job scheduler for daily generation and stream management."""

from __future__ import annotations

import datetime
import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from autostream.config import MUSIC_GEN_INTERVAL_HOURS, VISUAL_GEN_INTERVAL_HOURS
from autostream.db.models import Channel, SessionLocal, StreamLog
from autostream.stream_engine.engine import is_streaming, start_stream, stop_stream

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def _check_schedules() -> None:
    """Check all channels and start/stop streams based on schedule."""
    db = SessionLocal()
    try:
        channels = db.query(Channel).all()
        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M")

        for ch in channels:
            streaming = is_streaming(ch.id)

            if ch.is_24_7 and not streaming and ch.stream_key:
                logger.info("Auto-starting 24/7 channel %d: %s", ch.id, ch.name)
                start_stream(ch.id, ch.music_folder, ch.visual_folder, ch.stream_key, ch.playback_mode)
                ch.is_active = True
                db.add(StreamLog(channel_id=ch.id, level="info", message="Auto-started (24/7 mode)"))

            elif not ch.is_24_7 and ch.schedule_start and ch.schedule_stop:
                in_window = _time_in_range(ch.schedule_start, ch.schedule_stop, current_time)
                if in_window and not streaming and ch.stream_key:
                    logger.info("Schedule start channel %d: %s", ch.id, ch.name)
                    start_stream(ch.id, ch.music_folder, ch.visual_folder, ch.stream_key, ch.playback_mode)
                    ch.is_active = True
                    db.add(StreamLog(channel_id=ch.id, level="info", message=f"Scheduled start at {current_time}"))
                elif not in_window and streaming:
                    logger.info("Schedule stop channel %d: %s", ch.id, ch.name)
                    stop_stream(ch.id)
                    ch.is_active = False
                    db.add(StreamLog(channel_id=ch.id, level="info", message=f"Scheduled stop at {current_time}"))

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Schedule check failed")
    finally:
        db.close()


def _time_in_range(start: str, stop: str, current: str) -> bool:
    """Check if current HH:MM is between start and stop (handles midnight wrap)."""
    if start <= stop:
        return start <= current <= stop
    return current >= start or current <= stop


def _music_generation_job() -> None:
    """Placeholder for daily music generation."""
    logger.info("Music generation job triggered (stub)")


def _visual_generation_job() -> None:
    """Placeholder for daily visual generation."""
    logger.info("Visual generation job triggered (stub)")


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if scheduler.running:
        return

    # Check schedules every minute
    scheduler.add_job(
        _check_schedules,
        IntervalTrigger(minutes=1),
        id="check_schedules",
        replace_existing=True,
    )

    # Daily music generation at 03:00 UTC
    scheduler.add_job(
        _music_generation_job,
        CronTrigger(hour=3, minute=0),
        id="music_generation",
        replace_existing=True,
    )

    # Daily visual generation at 04:00 UTC
    scheduler.add_job(
        _visual_generation_job,
        CronTrigger(hour=4, minute=0),
        id="visual_generation",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs.", len(scheduler.get_jobs()))


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
    _scheduler = None
