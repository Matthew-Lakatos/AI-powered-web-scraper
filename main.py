"""
main.py
-------
Entry point for the scraping + NLP pipeline.

run_pipeline(urls) is the single public coroutine consumed by:
  - the CLI (cli.py)
  - the FastAPI background tasks (api.py)
  - direct invocation via __main__

Fix log
-------
- create_db() is now the very first thing run_pipeline() does so the
  cache check never races against a missing table on first run.
- analyze_all() now receives the source URL so credibility scoring
  inside the analyzer has a meaningful input.
- Removed re-import of compute_credibility / generate_embedding — both
  are now fully handled inside analyze_all(); duplicating them here
  produced double computation and a now-redundant embedding column.
- json.dumps() wrappers are applied here, at the DB boundary, so
  analyzer.py returns plain Python objects throughout.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import List, Optional

from analyzer import analyze_all
from cache import is_cache_valid, update_last_scraped
from config import settings
from crawler import crawl
from database import create_db, get_connection, save_many_to_db
from discovery import discover_urls
from logging_config import setup_logging
from monitor import Monitor, Timer
from scraper import scrape_all_urls

setup_logging()
logger = logging.getLogger(__name__)


DEFAULT_URLS: List[str] = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.bbc.com/news/technology",
    "https://www.theverge.com/tech",
]


# ---------------------------------------------------------------------------
# Discovery entry point
# ---------------------------------------------------------------------------

async def run_discovery(topic: str, max_pages: int = 50) -> None:
    urls = discover_urls(topic)
    crawled = await crawl(urls, max_pages=max_pages)
    await run_pipeline(crawled)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

async def run_pipeline(
    urls: List[str],
    monitor: Optional[Monitor] = None,
) -> None:
    """
    Full scrape → analyse → persist pipeline.

    Parameters
    ----------
    urls    : list of URLs to process.
    monitor : optional Monitor instance for timing/counting metrics.
    """

    # ------------------------------------------------------------------ #
    # 1. Ensure the DB schema exists BEFORE any cache lookup.             #
    #    On a fresh install the table doesn't exist yet; running          #
    #    is_cache_valid() before this call would throw OperationalError.  #
    # ------------------------------------------------------------------ #
    create_db()

    if monitor is None:
        monitor = Monitor()

    logger.info("Starting scraping pipeline for %d URL(s)", len(urls))

    # De-duplicate while preserving a consistent order.
    seen: set = set()
    unique_urls: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    # ------------------------------------------------------------------ #
    # 2. Cache filter — skip URLs scraped recently.                       #
    # ------------------------------------------------------------------ #
    urls_to_scrape: List[str] = []
    for url in unique_urls:
        if is_cache_valid(url):
            logger.info("Skipping (cached): %s", url)
            monitor.record_cached()
        else:
            urls_to_scrape.append(url)

    if not urls_to_scrape:
        logger.info("All URLs are within cache TTL — nothing to do.")
        return

    # ------------------------------------------------------------------ #
    # 3. Scrape                                                           #
    # ------------------------------------------------------------------ #
    with Timer() as t_scrape:
        scraped_data = await scrape_all_urls(urls_to_scrape)

    monitor.record_scrape(t_scrape.duration)
    logger.info(
        "Scraped %d URL(s) in %.2fs", len(scraped_data), t_scrape.duration
    )

    # ------------------------------------------------------------------ #
    # 4. Analyse + build rows for bulk insert                             #
    # ------------------------------------------------------------------ #
    rows_to_insert: List[tuple] = []

    for item in scraped_data:
        url  = item["url"]
        text = item.get("text") or ""

        if not text:
            logger.warning("Empty text for %s — skipping analysis", url)
            continue

        with Timer() as t_nlp:
            # Pass url so credibility scoring inside analyze_all has context.
            analysis = analyze_all(text, url=url)

        monitor.record_nlp(t_nlp.duration)

        # ---- Unpack the structured result ------------------------------ #
        sentiment  = analysis["sentiment"]    # {"label": str, "score": float}
        keywords   = analysis["keywords"]     # list[str]
        topics     = analysis["topics"]       # list[str]
        summary    = analysis["summary"]      # str
        emotions   = analysis["emotions"]     # dict[str, float|int]
        propaganda = analysis["propaganda"]   # {"score", "flags", ...}
        credibility = analysis["credibility"] # float
        embedding  = analysis.get("embedding")  # list[float] | None  (optional)

        # embedding may not always be present; generate it from summary if missing.
        if embedding is None:
            from embeddings import generate_embedding
            embedding = generate_embedding(summary or text[:1000])

        # ---- Build the 13-element DB row ------------------------------- #
        # Column order MUST match database.py:_INSERT_SQL exactly.
        rows_to_insert.append((
            url,                               #  1  url
            sentiment["label"],                #  2  sentiment
            sentiment["score"],                #  3  score
            text,                              #  4  text
            json.dumps(keywords),              #  5  keywords
            json.dumps(topics),                #  6  topics
            summary,                           #  7  summary
            json.dumps(emotions),              #  8  emotions
            json.dumps(embedding or []),       #  9  embedding
            credibility,                       # 10  credibility
            propaganda["score"],               # 11  propaganda_score
            json.dumps(propaganda["flags"]),   # 12  propaganda_flags
            datetime.utcnow().isoformat(),     # 13  last_scraped
        ))

    # ------------------------------------------------------------------ #
    # 5. Persist                                                          #
    # ------------------------------------------------------------------ #
    if rows_to_insert:
        with get_connection() as conn:
            save_many_to_db(conn, rows_to_insert)
            # Update the cache timestamp for every URL we just persisted.
            for row in rows_to_insert:
                update_last_scraped(conn, row[0])

        logger.info("Persisted %d record(s) to the database", len(rows_to_insert))

    logger.info(
        "Pipeline complete. %s",
        monitor.summary(),
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    urls = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_URLS
    asyncio.run(run_pipeline(urls))


if __name__ == "__main__":
    main()
