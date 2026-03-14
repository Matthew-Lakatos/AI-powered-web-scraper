from url_queue import URLQueue
from link_extractor import extract_links
from crawl_rules import is_content_url
from scraper import fetch_html
import asyncio


async def discover_urls(query):

    # use existing search logic
    urls = []

    try:
        urls = await search(query)
    except Exception:
        pass

    return urls


async def crawl(seed_urls, max_pages=50, content_only=False):

    queue = URLQueue()

    queue.add_many(seed_urls)

    discovered = []

    while not queue.empty() and len(discovered) < max_pages:

        url = queue.get()

        try:

            html = await fetch_html(url)

            links = extract_links(html, url)

            for link in links:

                if content_only:

                    if is_content_url(link):
                        queue.add(link)

                else:
                    queue.add(link)

        except Exception:
            continue

        discovered.append(url)

    return discovered
