from fastapi import FastAPI
from database import get_connection
import json

app = FastAPI(title="AI Web Scraper API")


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
            "keywords": json.loads(r[4]) if r[4] else [],
            "topics": json.loads(r[5]) if r[5] else [],
            "summary": r[6],
            "emotions": json.loads(r[7]) if r[7] else {},
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
