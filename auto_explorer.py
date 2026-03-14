import asyncio
import time

from target_profiles import TARGETS
from discovery_ai import build_queries
from crawler import discover_urls
from scraper import scrape_page
from analyzer import analyze_text
from narrative_engine import update_narratives
from knowledge_graph import link_entity_topic
from vector_store import store_embedding
from alert_engine import evaluate_narrative


class AutonomousExplorer:

    def __init__(self):

        self.visited_urls = set()
        self.discovered_topics = set()

    async def explore_target(self, target):

        name = target["name"]

        print(f"Exploring target: {name}")

        queries = build_queries(name)

        for query in queries:

            urls = await discover_urls(query)

            for url in urls:

                if url in self.visited_urls:
                    continue

                self.visited_urls.add(url)

                await self.process_url(url, name)

    async def process_url(self, url, target_name):

        try:

            page = await scrape_page(url)

            if not page or "text" not in page:
                return

            text = page["text"]

            analysis = analyze_text(text)

            # store embeddings
            store_embedding(text, metadata={"url": url})

            # narrative tracking
            narrative = update_narratives(analysis)

            # link knowledge graph
            topic = analysis.get("topic")

            if topic:
                link_entity_topic(target_name, topic)

            # alerts
            alerts = evaluate_narrative(narrative)

            if alerts:
                print(f"ALERT for {url}: {alerts}")

            # discover new topics
            self.expand_topics(analysis)

        except Exception as e:
            print("Explorer error:", e)

    def expand_topics(self, analysis):

        topics = analysis.get("keywords", [])

        for topic in topics:

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

            time.sleep(delay)


if __name__ == "__main__":

    explorer = AutonomousExplorer()

    asyncio.run(explorer.run_forever())
