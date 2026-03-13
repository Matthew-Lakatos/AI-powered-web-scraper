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
    """
    Creates the database table with all NLP extras included.
    Also performs safe migrations if columns already exist.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Base table creation
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                sentiment TEXT,
                score REAL,
                text TEXT,
                keywords TEXT,
                topics TEXT,
                summary TEXT,
                emotions TEXT,
                last_scraped TIMESTAMP
            )
            """
        )

        # Ensure index exists
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sentiment_url
            ON sentiment_data (url)
            """
        )

        # Safe migrations for older DB versions
        existing_cols = {
            row[1] for row in cursor.execute("PRAGMA table_info(sentiment_data)").fetchall()
        }

        migrations = {
            "keywords": "ALTER TABLE sentiment_data ADD COLUMN keywords TEXT",
            "topics": "ALTER TABLE sentiment_data ADD COLUMN topics TEXT",
            "summary": "ALTER TABLE sentiment_data ADD COLUMN summary TEXT",
            "emotions": "ALTER TABLE sentiment_data ADD COLUMN emotions TEXT",
            "last_scraped": "ALTER TABLE sentiment_data ADD COLUMN last_scraped TIMESTAMP",
        }

        for col, sql in migrations.items():
            if col not in existing_cols:
                cursor.execute(sql)

        conn.commit()


def save_many_to_db(
    conn: sqlite3.Connection,
    rows: Iterable[
        Tuple[
            str,   # url
            str,   # sentiment
            float, # score
            str,   # text
            str,   # keywords
            str,   # topics
            str,   # summary
            str,   # emotions
            str    # last_scraped timestamp
        ]
    ]
) -> None:
    """
    Batch insert rows with full NLP metadata.
    Expected row format:
    (
        url,
        sentiment,
        score,
        text,
        keywords,
        topics,
        summary,
        emotions,
        last_scraped
    )
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO sentiment_data
        (url, sentiment, score, text, keywords, topics, summary, emotions, last_scraped)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        list(rows),
    )
    conn.commit()


def fetch_all(conn: sqlite3.Connection) -> List[Tuple]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, url, sentiment, score, keywords, topics, summary, emotions, last_scraped
        FROM sentiment_data
        """
    )
    return cursor.fetchall()
