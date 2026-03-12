import asyncio
import os
import logging
from typing import List, Dict, Any, Optional

import aiohttp
from aiohttp import ClientError
from bs4 import BeautifulSoup
from readability import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

# limiting concurrent HTTP requests
_SEMAPHORE = asyncio.Semaphore(10)


def _get_chromedriver_path() -> Optional[str]:
    return os.getenv("CHROMEDRIVER_PATH")


def scrape_dynamic_content(url: str) -> str:
    """
    block Selenium based scraper in JS-heavy pages, run in thread
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver_path = _get_chromedriver_path()
    if driver_path:
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        driver.implicitly_wait(5)
        html = driver.page_source
    finally:
        driver.quit()

    # clean
    doc = Document(html)
    cleaned_html = doc.summary()
    soup = BeautifulSoup(cleaned_html, "html.parser")
    text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
    return text


async def _extract_text_from_html(html: str) -> str:
    # readability first then fall back to <p>
    try:
        doc = Document(html)
        cleaned_html = doc.summary()
        soup = BeautifulSoup(cleaned_html, "html.parser")
        paragraphs = soup.find_all("p")
        if paragraphs:
            return " ".join(p.get_text(strip=True) for p in paragraphs)
    except Exception as e:
        logger.debug(f"Readability failed, falling back to raw HTML parsing: {e}")

    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join(p.get_text(strip=True) for p in paragraphs)


async def scrape_url(url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """
    Scrape URL using aiohttp or Selenium.
    """
    async with _SEMAPHORE:
        logger.info(f"Scraping URL: {url}")
        try:
            async with session.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SentimentBot/1.0)"}
            ) as response:
                if response.status != 200:
                    logger.warning(f"Non-200 status for {url}: {response.status}")
                    return {"url": url, "text": "", "status": response.status}

                html = await response.text()
                text = await _extract_text_from_html(html)
                return {"url": url, "text": text, "status": response.status}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Error scraping {url}: {e}")
            return {"url": url, "text": "", "status": None}


async def scrape_all_urls(urls: List[str], use_dynamic_fallback: bool = True) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs concurrently. If a URL returns empty text and
    use_dynamic_fallback is True, attempt Selenium-based scraping in a thread.
    """
    # De-duplicate URLs
    unique_urls = list(dict.fromkeys(urls))

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url(url, session) for url in unique_urls]
        results = await asyncio.gather(*tasks)

    if use_dynamic_fallback:
        loop = asyncio.get_event_loop()
        for result in results:
            if not result.get("text"):
                url = result["url"]
                logger.info(f"Falling back to Selenium for {url}")
                try:
                    text = await loop.run_in_executor(None, scrape_dynamic_content, url)
                    result["text"] = text
                except Exception as e:
                    logger.error(f"Selenium fallback failed for {url}: {e}")

    return results
