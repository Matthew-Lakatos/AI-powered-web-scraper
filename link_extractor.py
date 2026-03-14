from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_links(html, base_url):

    soup = BeautifulSoup(html, "html.parser")

    links = []

    for tag in soup.find_all("a", href=True):

        link = urljoin(base_url, tag["href"])

        if link.startswith("http"):
            links.append(link)

    return links
