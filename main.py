import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import sys
import json

from crawler import crawl
from discovery import discover_urls
from scraper import scrape_all_urls
from analyzer import analyze_all
from database import create_db, get_connection, save_many_to_db
from cache import is_cache_valid, update_last_scraped
from config import settings
from logging_config import setup_logging
from monitor import Monitor, Timer

from embeddings import generate_embedding
from credibility import credibility_score

setup_logging()
logger = logging.getLogger(__name__)


DEFAULT_URLS = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.bbc.com/news/technology",
    "https://www.theverge.com/tech",
]


async def run_discovery(topic, max_pages=50):

    urls = discover_urls(topic)

    crawled = await crawl(urls, max_pages=max_pages)

    await run_pipeline(crawled)


async def run_pipeline(urls: List[str], monitor: Optional[Monitor] = None):

    if monitor is None:
        monitor = Monitor()

    logger.info("Starting scraping pipeline")

    urls = list(set(urls))

    urls_to_scrape = []

    for url in urls:

        if is_cache_valid(url):

            logger.info(f"Skipping (cached): {url}")

            monitor.record_cached()

        else:

            urls_to_scrape.append(url)

    if not urls_to_scrape:

        logger.info("All URLs cached")

        return

    with Timer() as t_scrape:

        scraped_data = await scrape_all_urls(urls_to_scrape)

    monitor.record_scrape(t_scrape.duration)

    rows_to_insert = []

    for item in scraped_data:

        url = item["url"]

        text = item.get("text", "") or ""

        with Timer() as t_nlp:

            analysis = analyze_all(text)

        monitor.record_nlp(t_nlp.duration)

        sentiment = analysis["sentiment"]

        keywords = analysis["keywords"]

        topics = analysis["topics"]

        summary = analysis["summary"]

        emotions = analysis["emotions"]

        embedding = generate_embedding(summary or text[:1000])

        credibility = credibility_score(url)

        rows_to_insert.append((

            url,

            sentiment["label"],

            sentiment["score"],

            text,

            json.dumps(keywords),

            json.dumps(topics),

            summary,

            json.dumps(emotions),

            json.dumps(embedding),

            credibility,

            datetime.utcnow().isoformat()

        ))

    create_db()

    with get_connection() as conn:

        save_many_to_db(conn, rows_to_insert)

        for row in rows_to_insert:

            update_last_scraped(conn, row[0])

    logger.info("Pipeline completed")


def main():

    urls = DEFAULT_URLS

    if len(sys.argv) > 1:

        urls = sys.argv[1:]

    asyncio.run(run_pipeline(urls))


if __name__ == "__main__":
    main()
