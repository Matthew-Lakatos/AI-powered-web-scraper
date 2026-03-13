from fastapi import FastAPI
from database import get_connection
import json

app = FastAPI(title="AI Web Scraper API")


def safe_parse(value):

    if value is None:
        return []

    try:
        return json.loads(value)
    except Exception:

        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]

        return value


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/results")
def get_results():

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            id,
            url,
            sentiment,
            score,
            keywords,
            topics,
            summary,
            emotions,
            last_scraped
        FROM sentiment_data
        ORDER BY last_scraped DESC
        """)

        rows = cursor.fetchall()

    results = []

    for r in rows:

        results.append({
            "id": r[0],
            "url": r[1],
            "sentiment": r[2],
            "score": r[3],
            "keywords": safe_parse(r[4]),
            "topics": safe_parse(r[5]),
            "summary": r[6],
            "emotions": safe_parse(r[7]),
            "last_scraped": r[8]
        })

    return {"results": results}


@app.get("/metrics")
def get_metrics():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sentiment_data")
        total = cursor.fetchone()[0]

        cursor.execute("""
        SELECT sentiment, COUNT(*)
        FROM sentiment_data
        GROUP BY sentiment
        """)

        sentiment_counts = dict(cursor.fetchall())

        cursor.execute("""
        SELECT COUNT(DISTINCT url)
        FROM sentiment_data
        """)

        unique_urls = cursor.fetchone()[0]

    return {
        "total_records": total,
        "unique_urls": unique_urls,
        "sentiment_breakdown": sentiment_counts
    }
