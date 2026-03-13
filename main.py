import asyncio
import logging
from typing import List

from scraper import scrape_all_urls
from analyzer import analyze_all
from database import create_db, get_connection, save_many_to_db


logging.basicConfig(
    level=logging.INFO,
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
    scraped_data = await scrape_all_urls(urls)

    rows_to_insert = []
    for item in scraped_data:
        url = item["url"]
        text = item.get("text", "") or ""

        full_analysis = analyze_all(text)
        sentiment = full_analysis["sentiment"]
        sentiment_label = sentiment["label"]
        sentiment_score = sentiment["score"]

        logger.info(
            f"URL: {url} | Sentiment: {sentiment_label} ({sentiment_score:.3f}) "
            f"| Topics: {full_analysis['topics']} "
            f"| Keywords: {full_analysis['keywords']}"
        )

        # DB schema unchanged: store sentiment + raw text
        rows_to_insert.append((url, sentiment_label, sentiment_score, text))

        # If you later extend DB, you can also store summary, topics, etc.

    create_db()
    with get_connection() as conn:
        save_many_to_db(conn, rows_to_insert)

    logger.info("Pipeline completed and data saved to database.")


def main():
    asyncio.run(run_pipeline(URLS))


if __name__ == "__main__":
    main()
