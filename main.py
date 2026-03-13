import asyncio
import logging
from typing import List
from datetime import datetime

from scraper import scrape_all_urls
from analyzer import analyze_all
from database import create_db, get_connection, save_many_to_db
from cache import is_cache_valid, update_last_scraped
from config import settings


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


URLS: List[str] = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.bbc.com/news/technology",
    "https://www.theverge.com/tech",
]


async def run_pipeline(urls: List[str]) -> None:
    logger.info("Starting scraping pipeline")

    urls_to_scrape = []
    for url in urls:
        if is_cache_valid(url):
            logger.info(f"Skipping (cached): {url}")
        else:
            urls_to_scrape.append(url)

    # If everything is cached, nothing to scrape
    if not urls_to_scrape:
        logger.info("All URLs are cached. Nothing to scrape.")
        return

    scraped_data = await scrape_all_urls(urls_to_scrape)

    rows_to_insert = []
    for item in scraped_data:
        url = item["url"]
        text = item.get("text", "") or ""

        full_analysis = analyze_all(text)

        sentiment = full_analysis["sentiment"]
        sentiment_label = sentiment["label"]
        sentiment_score = sentiment["score"]

        keywords = full_analysis["keywords"]
        topics = full_analysis["topics"]
        summary = full_analysis["summary"]
        emotions = full_analysis["emotions"]

        logger.info(
            f"URL: {url} | Sentiment: {sentiment_label} ({sentiment_score:.3f}) "
            f"| Topics: {topics} | Keywords: {keywords}"
        )

        # Store everything in the database
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

    create_db()
    with get_connection() as conn:
        save_many_to_db(conn, rows_to_insert)

        # Update last_scraped timestamps
        for row in rows_to_insert:
            update_last_scraped(conn, row[0])

    logger.info("Pipeline completed and data saved to database.")


def main():
    asyncio.run(run_pipeline(URLS))


if __name__ == "__main__":
    main()
