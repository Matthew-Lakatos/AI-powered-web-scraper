"""
database.py
-----------
SQLite persistence layer.

Schema
------
sentiment_data   — one row per scraped URL
narratives       — narrative cluster descriptions
knowledge_graph  — entity–topic edges

Public API
----------
create_db()
    Create all tables and indexes if they do not exist.
    Safe to call repeatedly — uses CREATE IF NOT EXISTS.
    Also runs add_missing_columns() so existing databases are
    upgraded automatically.

get_connection()
    Context manager yielding a sqlite3.Connection.
    Commits on success, rolls back on exception, always closes.

save_many_to_db(conn, rows)
    Bulk-insert rows into sentiment_data.
    Each row must be a 13-element tuple matching the column order
    documented in _INSERT_SQL below.

add_missing_columns(conn)
    ALTER TABLE to add any columns introduced after the initial
    schema was created (e.g. propaganda_score, propaganda_flags).
    Safe to run on already-upgraded databases.
"""

import logging
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = "scraped_data.db"

# ---------------------------------------------------------------------------
# Column order for sentiment_data INSERT (id is AUTOINCREMENT, excluded)
# ---------------------------------------------------------------------------
#  1  url
#  2  sentiment
#  3  score
#  4  text
#  5  keywords           (JSON-encoded list)
#  6  topics             (JSON-encoded list)
#  7  summary
#  8  emotions           (JSON-encoded dict)
#  9  embedding          (JSON-encoded list[float])
# 10  credibility
# 11  propaganda_score
# 12  propaganda_flags   (JSON-encoded list)
# 13  last_scraped       (ISO-8601 string)

_INSERT_SQL = """
    INSERT INTO sentiment_data (
        url, sentiment, score, text,
        keywords, topics, summary, emotions, embedding,
        credibility, propaganda_score, propaganda_flags,
        last_scraped
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# Columns added after the initial release — kept here so
# add_missing_columns() can apply them to older databases.
_MIGRATIONS: list[tuple[str, str]] = [
    ("propaganda_score", "REAL    DEFAULT 0.0"),
    ("propaganda_flags", "TEXT    DEFAULT '[]'"),
]


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

@contextmanager
def get_connection(db_path: str = DB_PATH):
    """
    Yield a sqlite3.Connection with WAL journal mode for better
    concurrent read performance.

    Commits on clean exit, rolls back on exception, always closes.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

def create_db(db_path: str = DB_PATH) -> None:
    """Create all tables and indexes. Safe to call on every startup."""
    with get_connection(db_path) as conn:
        _create_tables(conn)
        _create_indexes(conn)
        add_missing_columns(conn)
    logger.info("Database ready: %s", db_path)


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sentiment_data (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            url              TEXT    NOT NULL,
            sentiment        TEXT,
            score            REAL,
            text             TEXT,
            keywords         TEXT,
            topics           TEXT,
            summary          TEXT,
            emotions         TEXT,
            embedding        TEXT,
            credibility      REAL,
            propaganda_score REAL    DEFAULT 0.0,
            propaganda_flags TEXT    DEFAULT '[]',
            last_scraped     TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS narratives (
            id          INTEGER PRIMARY KEY,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS knowledge_graph (
            topic   TEXT NOT NULL,
            keyword TEXT NOT NULL
        );
    """)


def _create_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_url         ON sentiment_data(url);
        CREATE INDEX IF NOT EXISTS idx_sentiment   ON sentiment_data(sentiment);
        CREATE INDEX IF NOT EXISTS idx_credibility ON sentiment_data(credibility);
        CREATE INDEX IF NOT EXISTS idx_time        ON sentiment_data(last_scraped);
    """)


def add_missing_columns(conn: sqlite3.Connection) -> None:
    """
    Alter existing sentiment_data tables to add any columns that were
    introduced after the initial schema was deployed.

    Uses PRAGMA table_info() to detect which columns are already present
    so the ALTER TABLE is only executed when needed.
    """
    cursor = conn.execute("PRAGMA table_info(sentiment_data)")
    existing = {row[1] for row in cursor.fetchall()}

    for col_name, col_def in _MIGRATIONS:
        if col_name not in existing:
            sql = f"ALTER TABLE sentiment_data ADD COLUMN {col_name} {col_def}"
            conn.execute(sql)
            logger.info("Migration applied: added column '%s'", col_name)


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def save_many_to_db(conn: sqlite3.Connection, rows: list[tuple]) -> None:
    """
    Bulk-insert *rows* into sentiment_data.

    Each element of *rows* must be a 13-element tuple whose values
    match the column order defined in _INSERT_SQL above.

    Parameters
    ----------
    conn : sqlite3.Connection
        An open connection (typically obtained via get_connection()).
        The caller is responsible for committing / rolling back.
    rows : list[tuple]
        Rows to insert.  Empty list is a no-op.
    """
    if not rows:
        return

    # Validate arity before hitting the DB so the error message is clear.
    expected = 13
    bad = [(i, len(r)) for i, r in enumerate(rows) if len(r) != expected]
    if bad:
        raise ValueError(
            f"save_many_to_db: rows at indices {[i for i,_ in bad]} have wrong "
            f"length (expected {expected}): {bad[:3]}"
        )

    conn.executemany(_INSERT_SQL, rows)
    logger.debug("Inserted %d rows into sentiment_data", len(rows))
