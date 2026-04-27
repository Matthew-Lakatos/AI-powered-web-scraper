import asyncio
import time

from target_profiles import TARGETS
from discovery_ai import build_queries
from discovery import discover_urls
from scraper import scrape_all_urls
from analyzer import analyze_all
from narrative_engine import engine
from knowledge_graph import link_entity_topic
from vector_store import VectorStore
from alert_engine import evaluate_narrative
from embeddings import generate_embedding  # FIX: was imported inside method body

_vector_store = VectorStore()


class AutonomousExplorer:

    def __init__(self):
        self.visited_urls = set()
        self.discovered_topics = set()

    async def explore_target(self, target):

        name = target["name"]
        print(f"Exploring target: {name}")

        queries = build_queries(name)

        for query in queries:
            urls = discover_urls(query)           # sync function from discovery.py
            for url in urls:
                if url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                await self.process_url(url, name)

    async def process_url(self, url, target_name):

        try:
            # FIX: scrape_page did not exist — use scrape_all_urls and take first result
            results = await scrape_all_urls([url], use_dynamic_fallback=False)
            page = results[0] if results else None

            if not page or not page.get("text"):
                return

            text = page["text"]

            # FIX: was analyze_text — correct name is analyze_all
            analysis = analyze_all(text)

            # FIX: generate_embedding now imported at module top level
            embedding = generate_embedding(text[:500])
            if embedding:
                _vector_store.add(embedding, {"url": url})

            # FIX: update_narratives did not exist — use engine.add_article directly
            summary = analysis.get("summary", "")
            narrative_id = engine.add_article(text, summary)

            narrative = {
                "current_count": 1,
                "history": [],
                "sentiment": analysis["sentiment"]["score"],
                "previous_sentiment": None,
            }

            topic = analysis["topics"][0] if analysis.get("topics") else None
            if topic:
                link_entity_topic(target_name, topic)

            alerts = evaluate_narrative(narrative)
            if alerts:
                print(f"ALERT for {url}: {alerts}")

            self.expand_topics(analysis)

        except Exception as e:
            print("Explorer error:", e)

    def expand_topics(self, analysis):
        for topic in analysis.get("keywords", []):
            if topic not in self.discovered_topics:
                self.discovered_topics.add(topic)

    async def run_cycle(self):
        for target in TARGETS:
            await self.explore_target(target)

    async def run_forever(self, delay=1800):
        while True:
            print("Starting exploration cycle")
            await self.run_cycle()
            print("Cycle complete")
            await asyncio.sleep(delay)   # FIX: was time.sleep() (blocks the event loop)


if __name__ == "__main__":
    explorer = AutonomousExplorer()
    asyncio.run(explorer.run_forever())
