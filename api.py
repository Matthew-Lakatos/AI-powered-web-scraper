from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import json

from discovery import discover_urls
from crawler import crawl
from database import get_connection
from main import run_pipeline
from embeddings import generate_embedding
from vector_store import VectorStore

app = FastAPI(title="AI Web Scraper API")

# persistent vector store
vector_store = VectorStore()


# -------------------------
# REQUEST MODELS
# -------------------------

class URLRequest(BaseModel):
    urls: List[str]


class SemanticQuery(BaseModel):
    query: str
    k: Optional[int] = 5


# -------------------------
# HELPERS
# -------------------------

def safe_parse(value):

    if value is None:
        return []

    try:
        return json.loads(value)

    except Exception:

        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]

        return value


# -------------------------
# ROOT
# -------------------------

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

        # run pipeline on discovered pages
        run_pipeline(urls)

    background_tasks.add_task(task)

    return {"status": "crawl started"}


# -------------------------
# SEMANTIC SEARCH
# -------------------------

@app.get("/semantic-search")
def semantic_search(query: str, k: int = 5):

    embedding = generate_embedding(query)

    if embedding is None:
        return {"results": []}

    results = vector_store.search(embedding, k)

    return {
        "query": query,
        "results": results
    }


@app.post("/semantic-search")
def semantic_search_post(request: SemanticQuery):

    embedding = generate_embedding(request.query)

    if embedding is None:
        return {"results": []}

    results = vector_store.search(embedding, request.k)

    return {
        "query": request.query,
        "results": results
    }


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
            credibility,
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
            "credibility": r[8],
            "last_scraped": r[9]
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
