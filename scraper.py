"""
scraper.py
----------
Async HTTP scraper with readability-based text extraction and an
optional Selenium fallback for JS-heavy pages.

Fix log
-------
- Semaphore is now acquired *inside* the retry loop rather than around
  the entire loop.  The old placement held a concurrency slot for the
  duration of all retry attempts — a failed URL blocked a slot for up to
  2 × timeout (40 s) before releasing it, which starved the pool.
  With the fix each attempt acquires and releases independently so a
  transient failure does not tie up capacity.
- asyncio.get_running_loop() is used instead of the deprecated
  asyncio.get_event_loop() (Python ≥ 3.10 emits DeprecationWarning for
  the latter and 3.12 removes it for non-main threads).
- ClientTimeout object used throughout instead of bare integers.
- fetch_html() is the async helper consumed by crawler.py.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientError, ClientTimeout
from bs4 import BeautifulSoup
from readability import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

MAX_CONCURRENT = 20
RETRIES        = 2
RETRY_BACKOFF  = 1.0   # seconds to wait between retry attempts

semaphore = asyncio.Semaphore(MAX_CONCURRENT)

# ClientTimeout object — aiohttp rejects bare integers in newer versions.
_TIMEOUT = ClientTimeout(total=20)


# ---------------------------------------------------------------------------
# Dynamic (Selenium) fallback
# ---------------------------------------------------------------------------

def scrape_dynamic_content(url: str) -> str:
    """
    Render *url* with a headless Chrome instance and return extracted
    paragraph text.  Called in a thread executor so it never blocks the
    event loop.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()

    doc     = Document(html)
    cleaned = doc.summary()
    soup    = BeautifulSoup(cleaned, "html.parser")
    return " ".join(p.get_text(strip=True) for p in soup.find_all("p"))


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

async def _extract_text(html: str) -> str:
    """
    Extract readable paragraph text from raw HTML using python-readability
    with a BeautifulSoup fallback.
    """
    try:
        doc     = Document(html)
        cleaned = doc.summary()
        soup    = BeautifulSoup(cleaned, "html.parser")
        paragraphs = soup.find_all("p")
        if paragraphs:
            return " ".join(p.get_text(strip=True) for p in paragraphs)
    except Exception:
        pass

    # Plain fallback — no readability
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(p.get_text(strip=True) for p in soup.find_all("p"))


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

async def fetch_html(
    url: str,
    session: Optional[aiohttp.ClientSession] = None,
) -> str:
    """
    Fetch raw HTML for *url*.  Returns an empty string on any error.

    If *session* is not supplied a temporary one is created and closed
    after the request; pass a shared session when calling in a tight loop.
    """
    own_session = session is None
    if own_session:
        session = aiohttp.ClientSession()
    try:
        async with semaphore:
            async with session.get(url, timeout=_TIMEOUT) as response:
                if response.status == 200:
                    return await response.text()
                logger.debug("fetch_html: %s returned HTTP %d", url, response.status)
                return ""
    except Exception:
        logger.debug("fetch_html: error fetching %s", url, exc_info=True)
        return ""
    finally:
        if own_session:
            await session.close()


async def scrape_url(
    url: str,
    session: aiohttp.ClientSession,
) -> Dict[str, Any]:
    """
    Fetch and extract text from *url*, retrying up to RETRIES times.

    FIX: the semaphore is now acquired *inside* the retry loop so each
    attempt independently acquires and releases a concurrency slot.
    Previously the semaphore wrapped the whole loop, meaning a slow or
    failing URL held its slot across all retry attempts.

    Returns
    -------
    {"url": str, "text": str, "status": int | None}
    """
    for attempt in range(RETRIES):
        try:
            # FIX: semaphore acquired per-attempt, not per-URL-lifetime.
            async with semaphore:
                async with session.get(url, timeout=_TIMEOUT) as response:
                    if response.status != 200:
                        logger.debug(
                            "scrape_url: %s → HTTP %d (attempt %d)",
                            url, response.status, attempt + 1,
                        )
                        return {"url": url, "text": "", "status": response.status}
                    html = await response.text()
                    text = await _extract_text(html)
                    return {"url": url, "text": text, "status": response.status}

        except (ClientError, asyncio.TimeoutError) as exc:
            if attempt < RETRIES - 1:
                logger.debug(
                    "scrape_url: %s failed (%s) — retrying in %.1fs",
                    url, exc, RETRY_BACKOFF,
                )
                await asyncio.sleep(RETRY_BACKOFF)
            else:
                logger.warning("scrape_url: %s failed after %d attempts", url, RETRIES)
                return {"url": url, "text": "", "status": None}

    # Should be unreachable, but satisfies type checkers.
    return {"url": url, "text": "", "status": None}


# ---------------------------------------------------------------------------
# Batch entry point
# ---------------------------------------------------------------------------

async def scrape_all_urls(
    urls: List[str],
    use_dynamic_fallback: bool = True,
) -> List[Dict[str, Any]]:
    """
    Scrape all *urls* concurrently, optionally falling back to Selenium
    for pages that returned empty text.

    Parameters
    ----------
    urls                  : URLs to scrape.
    use_dynamic_fallback  : if True, pages with no extracted text are
                            retried with a headless Chrome instance.

    Returns
    -------
    List of {"url", "text", "status"} dicts in the same order as *urls*.
    """
    async with aiohttp.ClientSession() as session:
        tasks   = [scrape_url(u, session) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    if use_dynamic_fallback:
        # FIX: get_event_loop() is deprecated in Python 3.10+ for this use;
        # get_running_loop() returns the already-running loop safely.
        loop = asyncio.get_running_loop()
        for r in results:
            if not r["text"]:
                try:
                    text = await loop.run_in_executor(
                        None, scrape_dynamic_content, r["url"]
                    )
                    r["text"] = text or ""
                except Exception:
                    logger.debug(
                        "Dynamic fallback failed for %s", r["url"], exc_info=True
                    )

    return results
