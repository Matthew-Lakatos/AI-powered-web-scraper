import requests

SEARCH_TEMPLATES = [
    "{topic} news",
    "{topic} research",
    "{topic} analysis",
    "{topic} debate",
    "{topic} market impact"
]


def generate_queries(topic):

    return [t.format(topic=topic) for t in SEARCH_TEMPLATES]


def discover_urls(topic):

    queries = generate_queries(topic)

    urls = []

    for q in queries:

        try:

            res = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": q,
                    "format": "json"
                }
            )

            data = res.json()

            for r in data.get("RelatedTopics", []):

                if "FirstURL" in r:
                    urls.append(r["FirstURL"])

        except Exception:
            continue

    return list(set(urls))
