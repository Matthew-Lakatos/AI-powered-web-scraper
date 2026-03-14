CONTENT_PATTERNS = [
    "article",
    "news",
    "blog",
    "story",
    "post"
]


def is_content_url(url):

    url = url.lower()

    return any(p in url for p in CONTENT_PATTERNS)
