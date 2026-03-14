import asyncio
import logging
from typing import List, Dict, Any
import aiohttp
from aiohttp import ClientError
from bs4 import BeautifulSoup
from readability import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

MAX_CONCURRENT = 20
RETRIES = 2

semaphore = asyncio.Semaphore(MAX_CONCURRENT)


def scrape_dynamic_content(url: str):

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

    doc = Document(html)
    cleaned = doc.summary()

    soup = BeautifulSoup(cleaned, "html.parser")

    return " ".join(p.get_text(strip=True) for p in soup.find_all("p"))


async def _extract_text(html: str):

    try:

        doc = Document(html)
        cleaned = doc.summary()

        soup = BeautifulSoup(cleaned, "html.parser")

        paragraphs = soup.find_all("p")

        if paragraphs:
            return " ".join(p.get_text(strip=True) for p in paragraphs)

    except Exception:
        pass

    soup = BeautifulSoup(html, "html.parser")

    return " ".join(p.get_text(strip=True) for p in soup.find_all("p"))


async def scrape_url(url: str, session):

    async with semaphore:

        for attempt in range(RETRIES):

            try:

                async with session.get(url, timeout=20) as response:

                    if response.status != 200:
                        return {"url": url, "text": "", "status": response.status}

                    html = await response.text()

                    text = await _extract_text(html)

                    return {"url": url, "text": text, "status": response.status}

            except (ClientError, asyncio.TimeoutError):

                if attempt == RETRIES - 1:
                    return {"url": url, "text": "", "status": None}


async def scrape_all_urls(urls: List[str], use_dynamic_fallback=True):

    async with aiohttp.ClientSession() as session:

        tasks = [scrape_url(u, session) for u in urls]

        results = await asyncio.gather(*tasks)

    if use_dynamic_fallback:

        loop = asyncio.get_event_loop()

        for r in results:

            if not r["text"]:

                try:

                    text = await loop.run_in_executor(
                        None,
                        scrape_dynamic_content,
                        r["url"]
                    )

                    r["text"] = text

                except Exception:
                    pass

    return results
