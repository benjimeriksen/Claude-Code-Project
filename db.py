"""Database layer: creates the SQLite file and saves items into it.

Every source (GitHub, Reddit, YouTube, newsletters) is converted into the
same shape -- one row in the `items` table -- so we can filter, score and
search across all of them together.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "analyst.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL,   -- 'github', 'reddit', 'youtube', 'newsletter'
    external_id   TEXT NOT NULL,   -- the item's id on that source
    title         TEXT NOT NULL,
    url           TEXT NOT NULL,
    description   TEXT,
    author        TEXT,
    metrics       TEXT,            -- JSON: stars, upvotes, views... (differs per source)
    category      TEXT,            -- filled in later by categorize.py
    quality_score REAL,            -- 0-100, filled in later by scoring.py
    published_at  TEXT,            -- when the item was created at the source (ISO 8601)
    collected_at  TEXT NOT NULL,   -- when WE fetched it
    UNIQUE (source, external_id)   -- prevents duplicates when we re-run a collector
);
CREATE INDEX IF NOT EXISTS idx_items_source ON items (source);
CREATE INDEX IF NOT EXISTS idx_items_published ON items (published_at);
"""


def connect(path=DB_PATH):
    """Open the database (creating the file and tables if needed)."""
    path = Path(path)
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    conn.executescript(SCHEMA)
    return conn


def save_items(conn, items):
    """Insert items; if we've seen (source, external_id) before, update it.

    Re-running a collector refreshes star counts instead of making duplicates.
    Returns the number of items processed.
    """
    now = datetime.now(timezone.utc).isoformat()
    for item in items:
        conn.execute(
            """
            INSERT INTO items (source, external_id, title, url, description,
                               author, metrics, published_at, collected_at)
            VALUES (:source, :external_id, :title, :url, :description,
                    :author, :metrics, :published_at, :collected_at)
            ON CONFLICT (source, external_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                metrics = excluded.metrics,
                collected_at = excluded.collected_at
            """,
            {
                "description": None,
                "author": None,
                "published_at": None,
                **item,
                "metrics": json.dumps(item.get("metrics", {})),
                "collected_at": now,
            },
        )
    conn.commit()
    return len(items)
