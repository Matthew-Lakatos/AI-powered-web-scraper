from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import json

from discovery import discover_urls
from fastapi import BackgroundTasks
from crawler import crawl
from database import get_connection
from main import run_pipeline
from embeddings import generate_embedding
from vector_store import VectorStore

app = FastAPI(title="AI Web Scraper API")
vector_store = VectorStore()


class URLRequest(BaseModel):
    urls: List[str]


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


# -------------------------
# USER URL SUBMISSION
# -------------------------

@app.post("/analyze")
async def analyze_urls(request: URLRequest, background_tasks: BackgroundTasks):

    urls = list(set(request.urls))  # remove duplicates

    background_tasks.add_task(run_pipeline, urls)

    return {
        "status": "submitted",
        "urls": urls,
        "message": "URLs added to analysis queue"
    }

@app.post("/discover")
async def discover_topic(topic: str, background_tasks: BackgroundTasks):

    urls = discover_urls(topic)

    background_tasks.add_task(run_pipeline, urls)

    return {
        "topic": topic,
        "discovered_urls": urls[:10],
        "status": "submitted"
    }

@app.post("/crawl")
async def crawl_site(url: str, background_tasks: BackgroundTasks):

    async def task():

        urls = await crawl([url], max_pages=50)

        await run_pipeline(urls)

    background_tasks.add_task(task)

    return {"status": "crawl started"}

@app.get("/semantic-search")
def semantic_search(query: str):

    emb = generate_embedding(query)

    results = vector_store.search(emb)

    return {"results": results}

# -------------------------
# RESULTS
# -------------------------

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


# -------------------------
# METRICS
# -------------------------

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
