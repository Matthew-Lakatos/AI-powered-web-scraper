import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from config import settings
from database import get_connection


def get_last_scraped(url: str) -> Optional[datetime]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_scraped FROM sentiment_data WHERE url = ? ORDER BY id DESC LIMIT 1",
            (url,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None


def is_cache_valid(url: str) -> bool:
    last = get_last_scraped(url)
    if not last:
        return False

    expiry = last + timedelta(hours=settings.cache_expiry_hours)
    return datetime.utcnow() < expiry


def update_last_scraped(conn: sqlite3.Connection, url: str):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sentiment_data
        SET last_scraped = ?
        WHERE url = ?
        """,
        (datetime.utcnow().isoformat(), url)
    )
    conn.commit()
