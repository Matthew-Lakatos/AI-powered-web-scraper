import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import settings
from database import get_connection


def _now_utc() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def get_last_scraped(url: str) -> Optional[datetime]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_scraped FROM sentiment_data WHERE url = ? ORDER BY id DESC LIMIT 1",
            (url,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            dt = datetime.fromisoformat(row[0])
            # Stored timestamps may be naive (legacy rows written before the
            # timezone fix).  Treat any naive timestamp as UTC so comparisons
            # with timezone-aware datetimes don't raise TypeError.
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        return None


def is_cache_valid(url: str) -> bool:
    last = get_last_scraped(url)
    if not last:
        return False

    expiry = last + timedelta(hours=settings.cache_expiry_hours)
    return _now_utc() < expiry


def update_last_scraped(conn: sqlite3.Connection, url: str):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sentiment_data
        SET last_scraped = ?
        WHERE url = ?
        """,
        (_now_utc().isoformat(), url)
    )
    conn.commit()
