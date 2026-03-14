import tldextract

TRUSTED_DOMAINS = {
    "bbc.com": 0.9,
    "reuters.com": 0.9,
    "nature.com": 0.95,
    "arxiv.org": 0.9,
    "wikipedia.org": 0.85
}


def credibility_score(url: str) -> float:

    ext = tldextract.extract(url)

    domain = f"{ext.domain}.{ext.suffix}"

    score = 0.5

    if domain in TRUSTED_DOMAINS:
        score = TRUSTED_DOMAINS[domain]

    if ext.suffix in ["gov", "edu", "ac.uk"]:
        score += 0.2

    if "blogspot" in domain or "wordpress" in domain:
        score -= 0.3

    return max(0, min(score, 1))
