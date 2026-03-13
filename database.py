import sqlite3
from contextlib import contextmanager
from typing import Iterable, Tuple, List


DB_PATH = "scraped_data.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def create_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                sentiment TEXT,
                score REAL,
                text TEXT,
                last_scraped TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sentiment_url
            ON sentiment_data (url)
            """
        )
        conn.commit()


def save_many_to_db(
    conn: sqlite3.Connection,
    rows: Iterable[Tuple[str, str, float, str]]
) -> None:
    """
    Batch insert rows: (url, sentiment, score, text)
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO sentiment_data (url, sentiment, score, text)
        VALUES (?, ?, ?, ?)
        """,
        list(rows),
    )
    conn.commit()


def fetch_all(conn: sqlite3.Connection) -> List[Tuple]:
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, sentiment, score FROM sentiment_data")
    return cursor.fetchall()
