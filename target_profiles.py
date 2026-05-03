"""
target_profiles.py
------------------
Entity definitions for the scraping pipeline.

Structure
---------
Each target is a dict with:
    name       : display name / DB key
    type       : "company" | "index" | "macro" | "government"
    industry   : sector label
    ticker     : Yahoo Finance ticker symbol (None if not a traded instrument)
    keywords   : list of strings used by detect_targets() for mention matching
    news_urls  : curated high-signal URLs for this entity (scraped by default)

FINANCE_URLS / MACRO_URLS / GOVERNMENT_URLS
    Module-level lists of URLs that are always scraped in finance mode,
    regardless of specific target matching.  Imported by main.py.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# Target definitions
# ---------------------------------------------------------------------------

TARGETS = [

    # ---- Mega-cap tech (already present) --------------------------------- #
    {
        "name":      "Apple",
        "type":      "company",
        "industry":  "technology",
        "ticker":    "AAPL",
        "keywords":  ["Apple", "iPhone", "Tim Cook", "AAPL"],
        "news_urls": [
            "https://finance.yahoo.com/quote/AAPL/news/",
            "https://www.reuters.com/technology/",
        ],
    },
    {
        "name":      "NVIDIA",
        "type":      "company",
        "industry":  "semiconductors",
        "ticker":    "NVDA",
        "keywords":  ["NVIDIA", "GPU", "AI chips", "Jensen Huang", "NVDA"],
        "news_urls": [
            "https://finance.yahoo.com/quote/NVDA/news/",
            "https://www.reuters.com/technology/",
        ],
    },
    {
        "name":      "Tesla",
        "type":      "company",
        "industry":  "automotive",
        "ticker":    "TSLA",
        "keywords":  ["Tesla", "Elon Musk", "autonomous driving", "TSLA"],
        "news_urls": [
            "https://finance.yahoo.com/quote/TSLA/news/",
            "https://electrek.co/",
        ],
    },
    {
        "name":      "SpaceX",
        "type":      "company",
        "industry":  "aerospace",
        "ticker":    None,          # private company
        "keywords":  ["SpaceX", "Starship", "Falcon 9"],
        "news_urls": [
            "https://www.reuters.com/science/space/",
        ],
    },
    {
        "name":      "Google",
        "type":      "company",
        "industry":  "technology",
        "ticker":    "GOOGL",
        "keywords":  ["Google", "Alphabet", "Gemini AI", "GOOGL"],
        "news_urls": [
            "https://finance.yahoo.com/quote/GOOGL/news/",
        ],
    },
    {
        "name":      "Microsoft",
        "type":      "company",
        "industry":  "technology",
        "ticker":    "MSFT",
        "keywords":  ["Microsoft", "Azure", "OpenAI partnership", "MSFT"],
        "news_urls": [
            "https://finance.yahoo.com/quote/MSFT/news/",
        ],
    },
    {
        "name":      "OpenAI",
        "type":      "company",
        "industry":  "AI",
        "ticker":    None,          # private company
        "keywords":  ["OpenAI", "ChatGPT", "GPT models"],
        "news_urls": [
            "https://techcrunch.com/tag/openai/",
        ],
    },

    # ---- Additional high-value equities ---------------------------------- #
    {
        "name":      "Amazon",
        "type":      "company",
        "industry":  "ecommerce/cloud",
        "ticker":    "AMZN",
        "keywords":  ["Amazon", "AWS", "Jeff Bezos", "Andy Jassy", "AMZN"],
        "news_urls": [
            "https://finance.yahoo.com/quote/AMZN/news/",
        ],
    },
    {
        "name":      "Meta",
        "type":      "company",
        "industry":  "social media",
        "ticker":    "META",
        "keywords":  ["Meta", "Facebook", "Instagram", "Mark Zuckerberg", "META"],
        "news_urls": [
            "https://finance.yahoo.com/quote/META/news/",
        ],
    },
    {
        "name":      "JPMorgan",
        "type":      "company",
        "industry":  "banking",
        "ticker":    "JPM",
        "keywords":  ["JPMorgan", "JP Morgan", "Jamie Dimon", "JPM"],
        "news_urls": [
            "https://finance.yahoo.com/quote/JPM/news/",
            "https://www.ft.com/companies/banks",
        ],
    },

    # ---- Market indices -------------------------------------------------- #
    {
        "name":      "S&P 500",
        "type":      "index",
        "industry":  "broad market",
        "ticker":    "^GSPC",
        "keywords":  ["S&P 500", "S&P500", "SPX", "SPY", "broad market"],
        "news_urls": [
            "https://finance.yahoo.com/quote/%5EGSPC/news/",
            "https://www.marketwatch.com/investing/index/spx",
        ],
    },
    {
        "name":      "NASDAQ",
        "type":      "index",
        "industry":  "technology index",
        "ticker":    "^IXIC",
        "keywords":  ["NASDAQ", "Nasdaq Composite", "QQQ", "tech stocks"],
        "news_urls": [
            "https://finance.yahoo.com/quote/%5EIXIC/news/",
        ],
    },
    {
        "name":      "Dow Jones",
        "type":      "index",
        "industry":  "broad market",
        "ticker":    "^DJI",
        "keywords":  ["Dow Jones", "DJIA", "Dow 30", "DIA"],
        "news_urls": [
            "https://finance.yahoo.com/quote/%5EDJI/news/",
        ],
    },

    # ---- Macro / rates --------------------------------------------------- #
    {
        "name":      "Federal Reserve",
        "type":      "macro",
        "industry":  "monetary policy",
        "ticker":    None,
        "keywords":  ["Federal Reserve", "Fed", "Jerome Powell", "FOMC",
                      "interest rates", "rate hike", "rate cut"],
        "news_urls": [
            "https://www.federalreserve.gov/newsevents/pressreleases.htm",
            "https://www.reuters.com/markets/us/",
        ],
    },
    {
        "name":      "US Treasury",
        "type":      "macro",
        "industry":  "fiscal policy",
        "ticker":    None,
        "keywords":  ["US Treasury", "Treasury yield", "10-year yield",
                      "Janet Yellen", "Treasury bonds", "T-bills"],
        "news_urls": [
            "https://home.treasury.gov/news/press-releases",
            "https://finance.yahoo.com/quote/%5ETNX/",   # 10Y yield
        ],
    },

    # ---- Government spending --------------------------------------------- #
    {
        "name":      "US Federal Spending",
        "type":      "government",
        "industry":  "fiscal",
        "ticker":    None,
        "keywords":  ["federal spending", "government contract", "usaspending",
                      "defense spending", "federal budget", "appropriations"],
        "news_urls": [
            "https://www.usaspending.gov/explorer",
            "https://www.usaspending.gov/agency",
            "https://fiscaldata.treasury.gov/datasets/",
        ],
    },
    {
        "name":      "SEC Filings",
        "type":      "government",
        "industry":  "regulation",
        "ticker":    None,
        "keywords":  ["SEC filing", "10-K", "10-Q", "8-K", "earnings report",
                      "Securities and Exchange Commission"],
        "news_urls": [
            "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K",
            "https://efts.sec.gov/LATEST/search-index?q=%22earnings%22&dateRange=custom&startdt=2024-01-01&forms=8-K",
        ],
    },
]


# ---------------------------------------------------------------------------
# Curated URL lists imported by main.py
# ---------------------------------------------------------------------------

# High-frequency financial news — always included in finance pipeline runs
FINANCE_URLS: list[str] = [
    "https://finance.yahoo.com/news/",
    "https://www.reuters.com/markets/",
    "https://www.ft.com/markets",
    "https://www.marketwatch.com/latest-news",
    "https://www.bloomberg.com/markets",
    "https://www.cnbc.com/markets/",
    "https://seekingalpha.com/market-news",
]

# Macro-economic data sources
MACRO_URLS: list[str] = [
    "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    "https://home.treasury.gov/news/press-releases",
    "https://www.bls.gov/news.release/",          # BLS: CPI, jobs
    "https://fred.stlouisfed.org/",               # FRED economic data
    "https://fiscaldata.treasury.gov/datasets/",
]

# Government spending & contracts
GOVERNMENT_URLS: list[str] = [
    "https://www.usaspending.gov/explorer",
    "https://www.usaspending.gov/agency",
    "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K",
]

# All finance-mode URLs combined (de-duplicated)
ALL_FINANCE_URLS: list[str] = list(dict.fromkeys(
    FINANCE_URLS + MACRO_URLS + GOVERNMENT_URLS
))


# ---------------------------------------------------------------------------
# Ticker → name lookup (for price fetching)
# ---------------------------------------------------------------------------

TICKER_MAP: dict[str, str] = {
    t["ticker"]: t["name"]
    for t in TARGETS
    if t.get("ticker")
}


# ---------------------------------------------------------------------------
# Entity detection (used by analyzer.py)
# ---------------------------------------------------------------------------

def detect_targets(text: str) -> list[str]:
    """Return names of all targets mentioned in *text*."""
    text_lower = text.lower()
    matches = []
    for target in TARGETS:
        for keyword in target["keywords"]:
            if keyword.lower() in text_lower:
                matches.append(target["name"])
                break
    return matches
