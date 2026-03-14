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

        conn.commit()


def save_many_to_db(conn, rows):

    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO sentiment_data
        (url,sentiment,score,text,keywords,topics,summary,emotions,embedding,credibility,last_scraped)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        rows
    )

    conn.commit()
