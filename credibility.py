import re
from urllib.parse import urlparse

# -----------------------------
# HIGH TRUST DOMAINS
# -----------------------------

HIGH_TRUST_DOMAINS = {
    "bbc.com": 0.95,
    "reuters.com": 0.95,
    "apnews.com": 0.95,
    "nature.com": 0.95,
    "science.org": 0.95,
    "who.int": 0.95,
    "gov.uk": 0.95,
    "whitehouse.gov": 0.95,
    "nytimes.com": 0.9,
    "theguardian.com": 0.9,
    "washingtonpost.com": 0.9
}

# -----------------------------
# LOW TRUST DOMAINS
# -----------------------------

LOW_TRUST_PATTERNS = [
    "blogspot",
    "wordpress",
    "substack",
    "wixsite",
    "tumblr",
    "weebly"
]

# -----------------------------
# TLD TRUST SCORES
# -----------------------------

TLD_SCORES = {

    ".gov": 0.95,
    ".edu": 0.95,
    ".ac.uk": 0.95,
    ".int": 0.9,

    ".org": 0.75,
    ".co.uk": 0.75,

    ".com": 0.65,
    ".net": 0.6,

    ".info": 0.5
}


# -----------------------------
# DOMAIN EXTRACTION
# -----------------------------

def get_domain(url):

    parsed = urlparse(url)

    return parsed.netloc.lower()


# -----------------------------
# TLD DETECTION
# -----------------------------

def get_tld(domain):

    for tld in sorted(TLD_SCORES.keys(), key=len, reverse=True):

        if domain.endswith(tld):
            return tld

    return None


# -----------------------------
# DOMAIN SCORE
# -----------------------------

def score_domain(domain):

    for trusted in HIGH_TRUST_DOMAINS:

        if trusted in domain:
            return HIGH_TRUST_DOMAINS[trusted]

    for pattern in LOW_TRUST_PATTERNS:

        if pattern in domain:
            return 0.3

    return None


# -----------------------------
# CONTENT QUALITY
# -----------------------------

def score_content_quality(text):

    if not text:
        return 0.3

    words = text.split()

    length_score = min(len(words) / 800, 1.0)

    unique_ratio = len(set(words)) / max(len(words), 1)

    diversity_score = min(unique_ratio * 2, 1.0)

    return (length_score + diversity_score) / 2


# -----------------------------
# MAIN SCORING FUNCTION
# -----------------------------

def compute_credibility(url, text):

    domain = get_domain(url)

    domain_score = score_domain(domain)

    if domain_score is None:

        tld = get_tld(domain)

        if tld:
            domain_score = TLD_SCORES.get(tld, 0.6)

        else:
            domain_score = 0.6

    content_score = score_content_quality(text)

    final_score = (domain_score * 0.7) + (content_score * 0.3)

    final_score = max(0.0, min(1.0, final_score))

    return round(final_score, 3)
