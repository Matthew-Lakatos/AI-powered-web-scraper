import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import sys

from crawler import crawl
from discovery import discover_urls
from scraper import scrape_all_urls
from analyzer import analyze_all
from database import create_db, get_connection, save_many_to_db
from cache import is_cache_valid, update_last_scraped
from config import settings
from logging_config import setup_logging
from monitor import Monitor, Timer


setup_logging()
logger = logging.getLogger(__name__)


DEFAULT_URLS: List[str] = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.bbc.com/news/technology",
    "https://www.theverge.com/tech",
]

async def run_discovery(topic, max_pages=50):

    urls = discover_urls(topic)

    crawled = await crawl(urls, max_pages=max_pages)

    await run_pipeline(crawled)


async def run_pipeline(
    urls: List[str],
    monitor: Optional[Monitor] = None
) -> None:

    if monitor is None:
        monitor = Monitor()

    logger.info("Starting scraping pipeline")

    # remove duplicates
    urls = list(set(urls))

    # Step 1 — caching
    urls_to_scrape = []

    for url in urls:

        if is_cache_valid(url):
            logger.info(f"Skipping (cached): {url}")
            monitor.record_cached()

        else:
            urls_to_scrape.append(url)

    if not urls_to_scrape:

        logger.info("All URLs cached.")
        logger.info(f"Monitor summary: {monitor.summary()}")
        return

    # Step 2 — scrape
    with Timer() as t_scrape:
        scraped_data = await scrape_all_urls(urls_to_scrape)

    monitor.record_scrape(t_scrape.duration)

    # Step 3 — analyze
    rows_to_insert = []

    for item in scraped_data:

        url = item["url"]
        text = item.get("text", "") or ""

        with Timer() as t_nlp:
            full_analysis = analyze_all(text)

        monitor.record_nlp(t_nlp.duration)

        sentiment = full_analysis["sentiment"]

        sentiment_label = sentiment["label"]
        sentiment_score = sentiment["score"]

        keywords = full_analysis["keywords"]
        topics = full_analysis["topics"]
        summary = full_analysis["summary"]
        emotions = full_analysis["emotions"]

        logger.info(
            f"{url} | Sentiment: {sentiment_label} ({sentiment_score:.3f})"
        )

        rows_to_insert.append((

            url,
            sentiment_label,
            sentiment_score,
            text,
            ", ".join(keywords),
            ", ".join(topics),
            summary,
            str(emotions),
            datetime.utcnow().isoformat()

        ))

    # Step 4 — DB
    create_db()

    with get_connection() as conn:

        save_many_to_db(conn, rows_to_insert)

        for row in rows_to_insert:
            update_last_scraped(conn, row[0])

    logger.info("Pipeline completed")
    logger.info(f"Monitor summary: {monitor.summary()}")


def main():

    urls = DEFAULT_URLS

    if len(sys.argv) > 1:
        urls = sys.argv[1:]

    asyncio.run(run_pipeline(urls))


if __name__ == "__main__":
    main()
