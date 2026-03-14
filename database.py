import sqlite3
from contextlib import contextmanager

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

            keywords TEXT,

            topics TEXT,

            summary TEXT,

            emotions TEXT,

            embedding TEXT,

            credibility REAL,

            last_scraped TIMESTAMP
        )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON sentiment_data(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON sentiment_data(sentiment)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_credibility ON sentiment_data(credibility)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON sentiment_data(last_scraped)")

        conn.commit()
