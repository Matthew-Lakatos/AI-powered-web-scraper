"""
auto_explorer.py
----------------
Autonomous exploration loop: iterates over tracked target profiles,
discovers URLs via AI-expanded queries, scrapes and analyses each page,
feeds results into the narrative engine and vector store, and fires
alerts when significant patterns are detected.

Fix log
-------
- asyncio.sleep() replaces time.sleep() so the event loop is not blocked.
- scrape_all_urls() replaces the non-existent scrape_page().
- analyze_all() replaces the non-existent analyze_text().
- engine.add_article() replaces the non-existent update_narratives().
- generate_embedding() is imported at module level (was inside method body).
- analyze_all() now receives the source URL for credibility scoring.
- analysis["sentiment"] is accessed as a dict {"label", "score"} to match
  the fixed analyzer.py return structure.
"""

import asyncio
import logging

from alert_engine import evaluate_narrative
from analyzer import analyze_all
from discovery import discover_urls
from discovery_ai import build_queries
from embeddings import generate_embedding
from knowledge_graph import link_entity_topic
from narrative_engine import engine
from scraper import scrape_all_urls
from target_profiles import TARGETS
from vector_store import VectorStore

logger = logging.getLogger(__name__)

_vector_store = VectorStore()


class AutonomousExplorer:

    def __init__(self) -> None:
        self.visited_urls: set[str] = set()
        self.discovered_topics: set[str] = set()

    # ------------------------------------------------------------------
    # Target iteration
    # ------------------------------------------------------------------

    async def explore_target(self, target: dict) -> None:
        name = target["name"]
        logger.info("Exploring target: %s", name)

        queries = build_queries(name)

        for query in queries:
            urls = discover_urls(query)          # sync helper from discovery.py
            for url in urls:
                if url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                await self.process_url(url, name)

    # ------------------------------------------------------------------
    # Single-URL processing
    # ------------------------------------------------------------------

    async def process_url(self, url: str, target_name: str) -> None:
        try:
            # FIX: scrape_page() did not exist — use scrape_all_urls() and
            # take the first result.  use_dynamic_fallback=False keeps the
            # explorer fast; Selenium fallback is reserved for main pipeline.
            results = await scrape_all_urls([url], use_dynamic_fallback=False)
            page = results[0] if results else None

            if not page or not page.get("text"):
                return

            text: str = page["text"]

            # FIX: analyze_text() did not exist — correct name is analyze_all().
            # Pass url so credibility scoring inside analyzer has context.
            analysis = analyze_all(text, url=url)

            # ---- Vector store ---------------------------------------- #
            # FIX: generate_embedding() was imported inside the method body;
            # it is now imported at module level.
            embedding = generate_embedding(text[:500])
            if embedding:
                _vector_store.add(embedding, {"url": url})

            # ---- Narrative engine ------------------------------------ #
            # FIX: update_narratives() did not exist — use engine.add_article().
            summary = analysis.get("summary", "")
            narrative_id = engine.add_article(text, summary)

            # ---- Alert evaluation ------------------------------------ #
            # FIX: analysis["sentiment"] is now a dict {"label", "score"};
            # access .score via the "score" key.
            narrative_payload = {
                "current_count":      1,
                "history":            [],
                "sentiment":          analysis["sentiment"]["score"],
                "previous_sentiment": None,
            }

            alerts = evaluate_narrative(narrative_payload)
            if alerts:
                logger.warning("ALERT for %s: %s", url, alerts)

            # ---- Knowledge graph links ------------------------------- #
            topics = analysis.get("topics", [])
            if topics:
                link_entity_topic(target_name, topics[0])

            # ---- Topic expansion ------------------------------------ #
            self._expand_topics(analysis)

        except Exception:
            logger.exception("Explorer error processing %s", url)

    # ------------------------------------------------------------------
    # Topic discovery
    # ------------------------------------------------------------------

    def _expand_topics(self, analysis: dict) -> None:
        for keyword in analysis.get("keywords", []):
            if keyword not in self.discovered_topics:
                self.discovered_topics.add(keyword)
                logger.debug("Discovered new topic keyword: %s", keyword)

    # ------------------------------------------------------------------
    # Cycle control
    # ------------------------------------------------------------------

    async def run_cycle(self) -> None:
        for target in TARGETS:
            await self.explore_target(target)

    async def run_forever(self, delay: int = 1800) -> None:
        """
        Run exploration cycles indefinitely, sleeping *delay* seconds
        between each cycle.

        FIX: was time.sleep(delay) which blocks the entire event loop.
        asyncio.sleep() yields control so other coroutines can run.
        """
        while True:
            logger.info("Starting exploration cycle")
            await self.run_cycle()
            logger.info(
                "Cycle complete. %d URLs visited, %d topics discovered.",
                len(self.visited_urls),
                len(self.discovered_topics),
            )
            await asyncio.sleep(delay)


if __name__ == "__main__":
    explorer = AutonomousExplorer()
    asyncio.run(explorer.run_forever())
