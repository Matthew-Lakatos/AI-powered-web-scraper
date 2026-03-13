from fastapi import FastAPI
from database import get_connection
from monitor import Monitor
from main import run_pipeline
import asyncio

app = FastAPI()
monitor = Monitor()

@app.get("/results")
def get_results():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url, sentiment, score, keywords, topics, summary, emotions, last_scraped
            FROM sentiment_data
            ORDER BY last_scraped DESC
        """)
        rows = cursor.fetchall()
    return {"results": rows}

@app.get("/stats")
def get_stats():
    return monitor.summary()

@app.post("/scrape")
async def scrape_urls(urls: list[str]):
    await run_pipeline(urls, monitor=monitor)
    return {"status": "completed"}
