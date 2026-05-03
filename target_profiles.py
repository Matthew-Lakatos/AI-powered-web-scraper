"""
target_profiles.py
------------------
Ultra-robust quant-grade target universe + structured data sources.

Focus:
- Equities / indices / ETFs
- AI ecosystem
- Defence / government spend
- Macro / rates / inflation
- UK / EU / China / global data
- Energy / biotech / weather / commodities
- Rich news_urls + data_urls populated wherever practical

Schema:
    name
    type
    industry
    ticker
    keywords
    news_urls
    data_urls
    priority      # 1-5
    tags
"""

from typing import Optional


# =====================================================================
# TARGETS
# =====================================================================

TARGETS = [

# ---------------------------------------------------------------------
# US BIG TECH / AI
# ---------------------------------------------------------------------

{
    "name": "Apple",
    "type": "company",
    "industry": "technology",
    "ticker": "AAPL",
    "keywords": ["Apple", "AAPL", "iPhone", "Tim Cook"],
    "news_urls": [
        "https://finance.yahoo.com/quote/AAPL/news/",
        "https://www.reuters.com/technology/",
        "https://www.macrumors.com/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 4,
    "tags": ["hardware", "consumer", "mega-cap"],
},

{
    "name": "Microsoft",
    "type": "company",
    "industry": "cloud/software",
    "ticker": "MSFT",
    "keywords": ["Microsoft", "MSFT", "Azure", "Satya Nadella", "OpenAI"],
    "news_urls": [
        "https://finance.yahoo.com/quote/MSFT/news/",
        "https://www.reuters.com/technology/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
        "https://azure.microsoft.com/en-gb/blog/",
    ],
    "priority": 5,
    "tags": ["ai", "cloud", "mega-cap"],
},

{
    "name": "NVIDIA",
    "type": "company",
    "industry": "semiconductors",
    "ticker": "NVDA",
    "keywords": ["NVIDIA", "NVDA", "GPU", "Jensen Huang"],
    "news_urls": [
        "https://finance.yahoo.com/quote/NVDA/news/",
        "https://www.reuters.com/technology/",
        "https://www.tomshardware.com/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 5,
    "tags": ["ai", "chips", "momentum"],
},

{
    "name": "Amazon",
    "type": "company",
    "industry": "cloud/ecommerce",
    "ticker": "AMZN",
    "keywords": ["Amazon", "AMZN", "AWS"],
    "news_urls": [
        "https://finance.yahoo.com/quote/AMZN/news/",
        "https://www.reuters.com/technology/",
    ],
    "data_urls": [
        "https://aws.amazon.com/blogs/aws/",
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 5,
    "tags": ["cloud", "consumer"],
},

{
    "name": "Google",
    "type": "company",
    "industry": "internet/cloud",
    "ticker": "GOOGL",
    "keywords": ["Google", "Alphabet", "GOOGL", "Gemini", "DeepMind"],
    "news_urls": [
        "https://finance.yahoo.com/quote/GOOGL/news/",
        "https://blog.google/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 5,
    "tags": ["ai", "search", "cloud"],
},

{
    "name": "Meta",
    "type": "company",
    "industry": "social media",
    "ticker": "META",
    "keywords": ["Meta", "META", "Facebook", "Instagram", "Llama"],
    "news_urls": [
        "https://finance.yahoo.com/quote/META/news/",
        "https://about.fb.com/news/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 4,
    "tags": ["ai", "ads"],
},

{
    "name": "Tesla",
    "type": "company",
    "industry": "automotive",
    "ticker": "TSLA",
    "keywords": ["Tesla", "TSLA", "Elon Musk", "robotaxi", "FSD"],
    "news_urls": [
        "https://finance.yahoo.com/quote/TSLA/news/",
        "https://electrek.co/",
        "https://www.reuters.com/business/autos-transportation/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 5,
    "tags": ["ev", "ai", "momentum"],
},

# ---------------------------------------------------------------------
# PRIVATE AI / GLOBAL AI
# ---------------------------------------------------------------------

{
    "name": "OpenAI",
    "type": "company",
    "industry": "AI",
    "ticker": None,
    "keywords": ["OpenAI", "ChatGPT", "GPT-5", "GPT"],
    "news_urls": [
        "https://techcrunch.com/tag/openai/",
        "https://openai.com/blog/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["private", "ai"],
},

{
    "name": "Anthropic",
    "type": "company",
    "industry": "AI",
    "ticker": None,
    "keywords": ["Anthropic", "Claude"],
    "news_urls": [
        "https://www.anthropic.com/news",
        "https://techcrunch.com/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["private", "ai"],
},

{
    "name": "xAI",
    "type": "company",
    "industry": "AI",
    "ticker": None,
    "keywords": ["xAI", "Grok"],
    "news_urls": [
        "https://x.ai/",
        "https://www.reuters.com/technology/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["private", "ai"],
},

{
    "name": "DeepSeek",
    "type": "company",
    "industry": "AI",
    "ticker": None,
    "keywords": ["DeepSeek", "DeepSeek AI"],
    "news_urls": [
        "https://www.scmp.com/",
        "https://www.reuters.com/world/china/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["china", "ai"],
},

{
    "name": "Alibaba",
    "type": "company",
    "industry": "china tech",
    "ticker": "BABA",
    "keywords": ["Alibaba", "BABA", "AliCloud"],
    "news_urls": [
        "https://finance.yahoo.com/quote/BABA/news/",
        "https://www.reuters.com/world/china/",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 4,
    "tags": ["china", "cloud"],
},

{
    "name": "Tencent",
    "type": "company",
    "industry": "china tech",
    "ticker": "TCEHY",
    "keywords": ["Tencent", "WeChat", "TCEHY"],
    "news_urls": [
        "https://finance.yahoo.com/quote/TCEHY/news/",
        "https://www.reuters.com/world/china/",
    ],
    "data_urls": [],
    "priority": 4,
    "tags": ["china", "ai"],
},

# ---------------------------------------------------------------------
# DEFENCE / GOV TECH
# ---------------------------------------------------------------------

{
    "name": "Lockheed Martin",
    "type": "company",
    "industry": "defence",
    "ticker": "LMT",
    "keywords": ["Lockheed", "Lockheed Martin", "LMT"],
    "news_urls": [
        "https://finance.yahoo.com/quote/LMT/news/",
        "https://www.defensenews.com/",
    ],
    "data_urls": [
        "https://api.usaspending.gov/api/v2/awards/",
    ],
    "priority": 5,
    "tags": ["contracts", "defence"],
},

{
    "name": "Raytheon",
    "type": "company",
    "industry": "defence",
    "ticker": "RTX",
    "keywords": ["Raytheon", "RTX"],
    "news_urls": [
        "https://finance.yahoo.com/quote/RTX/news/",
        "https://www.defensenews.com/",
    ],
    "data_urls": [
        "https://api.usaspending.gov/api/v2/awards/",
    ],
    "priority": 5,
    "tags": ["contracts"],
},

{
    "name": "Northrop Grumman",
    "type": "company",
    "industry": "defence",
    "ticker": "NOC",
    "keywords": ["Northrop", "NOC"],
    "news_urls": [
        "https://finance.yahoo.com/quote/NOC/news/",
    ],
    "data_urls": [
        "https://api.usaspending.gov/api/v2/awards/",
    ],
    "priority": 4,
    "tags": ["contracts"],
},

{
    "name": "Palantir",
    "type": "company",
    "industry": "software/defence",
    "ticker": "PLTR",
    "keywords": ["Palantir", "PLTR"],
    "news_urls": [
        "https://finance.yahoo.com/quote/PLTR/news/",
    ],
    "data_urls": [
        "https://api.usaspending.gov/api/v2/awards/",
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 5,
    "tags": ["ai", "government"],
},

# ---------------------------------------------------------------------
# FINANCIALS
# ---------------------------------------------------------------------

{
    "name": "JPMorgan",
    "type": "company",
    "industry": "banking",
    "ticker": "JPM",
    "keywords": ["JPMorgan", "JPM", "Jamie Dimon"],
    "news_urls": [
        "https://finance.yahoo.com/quote/JPM/news/",
        "https://www.ft.com/companies/banks",
    ],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
    ],
    "priority": 3,
    "tags": ["banking"],
},

# ---------------------------------------------------------------------
# INDICES / ETFS
# ---------------------------------------------------------------------

{
    "name": "S&P 500",
    "type": "index",
    "industry": "broad market",
    "ticker": "^GSPC",
    "keywords": ["S&P 500", "SPX", "SPY"],
    "news_urls": [
        "https://finance.yahoo.com/quote/%5EGSPC/news/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["benchmark"],
},

{
    "name": "NASDAQ",
    "type": "index",
    "industry": "technology",
    "ticker": "^IXIC",
    "keywords": ["NASDAQ", "QQQ"],
    "news_urls": [
        "https://finance.yahoo.com/quote/%5EIXIC/news/",
    ],
    "data_urls": [],
    "priority": 5,
    "tags": ["benchmark"],
},

{
    "name": "Dow Jones",
    "type": "index",
    "industry": "broad market",
    "ticker": "^DJI",
    "keywords": ["Dow Jones", "DJIA"],
    "news_urls": [
        "https://finance.yahoo.com/quote/%5EDJI/news/",
    ],
    "data_urls": [],
    "priority": 4,
    "tags": ["benchmark"],
},

{
    "name": "ITA",
    "type": "index",
    "industry": "defence ETF",
    "ticker": "ITA",
    "keywords": ["ITA"],
    "news_urls": [
        "https://finance.yahoo.com/quote/ITA/news/",
    ],
    "data_urls": [],
    "priority": 4,
    "tags": ["defence"],
},

# ---------------------------------------------------------------------
# MACRO / CENTRAL BANKS
# ---------------------------------------------------------------------

{
    "name": "Federal Reserve",
    "type": "macro",
    "industry": "rates",
    "ticker": None,
    "keywords": ["Federal Reserve", "Fed", "FOMC", "Powell"],
    "news_urls": [
        "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    ],
    "data_urls": [
        "https://fred.stlouisfed.org/",
    ],
    "priority": 5,
    "tags": ["rates", "us"],
},

{
    "name": "Bank of England",
    "type": "macro",
    "industry": "rates",
    "ticker": None,
    "keywords": ["Bank of England", "BoE"],
    "news_urls": [
        "https://www.bankofengland.co.uk/news",
    ],
    "data_urls": [
        "https://www.bankofengland.co.uk/statistics",
    ],
    "priority": 5,
    "tags": ["uk", "rates"],
},

{
    "name": "European Central Bank",
    "type": "macro",
    "industry": "rates",
    "ticker": None,
    "keywords": ["ECB", "European Central Bank"],
    "news_urls": [
        "https://www.ecb.europa.eu/press/html/index.en.html",
    ],
    "data_urls": [
        "https://www.ecb.europa.eu/stats/",
    ],
    "priority": 5,
    "tags": ["eu", "rates"],
},

# ---------------------------------------------------------------------
# DATASETS
# ---------------------------------------------------------------------

{
    "name": "US Federal Spending",
    "type": "dataset",
    "industry": "contracts",
    "ticker": None,
    "keywords": ["usaspending", "contract award"],
    "news_urls": [],
    "data_urls": [
        "https://api.usaspending.gov/api/v2/awards/",
        "https://www.usaspending.gov/",
    ],
    "priority": 5,
    "tags": ["alpha", "government"],
},

{
    "name": "SEC EDGAR",
    "type": "dataset",
    "industry": "filings",
    "ticker": None,
    "keywords": ["8-K", "10-Q", "10-K", "SEC"],
    "news_urls": [],
    "data_urls": [
        "https://www.sec.gov/edgar/search/",
        "https://www.sec.gov/Archives/edgar/data/",
    ],
    "priority": 5,
    "tags": ["earnings"],
},

{
    "name": "FRED Economic Data",
    "type": "dataset",
    "industry": "macro",
    "ticker": None,
    "keywords": ["FRED", "GDP", "yield curve", "recession"],
    "news_urls": [],
    "data_urls": [
        "https://fred.stlouisfed.org/",
        "https://api.stlouisfed.org/",
    ],
    "priority": 5,
    "tags": ["macro"],
},

{
    "name": "BLS Releases",
    "type": "dataset",
    "industry": "inflation/jobs",
    "ticker": None,
    "keywords": ["CPI", "PPI", "Payrolls", "NFP"],
    "news_urls": [],
    "data_urls": [
        "https://www.bls.gov/news.release/",
        "https://download.bls.gov/pub/time.series/",
    ],
    "priority": 5,
    "tags": ["macro"],
},

{
    "name": "ONS UK",
    "type": "dataset",
    "industry": "uk macro",
    "ticker": None,
    "keywords": ["ONS", "UK CPI", "UK GDP"],
    "news_urls": [],
    "data_urls": [
        "https://www.ons.gov.uk/",
    ],
    "priority": 5,
    "tags": ["uk"],
},

{
    "name": "Eurostat",
    "type": "dataset",
    "industry": "eu macro",
    "ticker": None,
    "keywords": ["Eurostat"],
    "news_urls": [],
    "data_urls": [
        "https://ec.europa.eu/eurostat",
    ],
    "priority": 5,
    "tags": ["eu"],
},

{
    "name": "UK Contracts Finder",
    "type": "dataset",
    "industry": "uk contracts",
    "ticker": None,
    "keywords": ["Contracts Finder"],
    "news_urls": [],
    "data_urls": [
        "https://www.contractsfinder.service.gov.uk/",
    ],
    "priority": 5,
    "tags": ["uk", "alpha"],
},

{
    "name": "EU TED Tenders",
    "type": "dataset",
    "industry": "eu contracts",
    "ticker": None,
    "keywords": ["TED", "EU tenders"],
    "news_urls": [],
    "data_urls": [
        "https://ted.europa.eu/",
    ],
    "priority": 5,
    "tags": ["eu", "alpha"],
},

{
    "name": "FDA Approvals",
    "type": "dataset",
    "industry": "biotech",
    "ticker": None,
    "keywords": ["FDA approval"],
    "news_urls": [],
    "data_urls": [
        "https://open.fda.gov/",
    ],
    "priority": 5,
    "tags": ["healthcare"],
},

{
    "name": "EIA Energy Data",
    "type": "dataset",
    "industry": "energy",
    "ticker": None,
    "keywords": ["oil inventory", "natural gas", "EIA"],
    "news_urls": [],
    "data_urls": [
        "https://www.eia.gov/opendata/",
    ],
    "priority": 4,
    "tags": ["commodities"],
},

{
    "name": "NOAA Weather",
    "type": "dataset",
    "industry": "weather",
    "ticker": None,
    "keywords": ["weather", "hurricane", "crop"],
    "news_urls": [],
    "data_urls": [
        "https://www.noaa.gov/",
        "https://www.weather.gov/",
    ],
    "priority": 4,
    "tags": ["agriculture"],
},

]


# =====================================================================
# ALWAYS SCRAPED URLS
# =====================================================================

FINANCE_URLS = [
    "https://finance.yahoo.com/news/",
    "https://www.reuters.com/markets/",
    "https://www.ft.com/markets",
    "https://www.marketwatch.com/latest-news",
    "https://www.cnbc.com/markets/",
    "https://seekingalpha.com/market-news",
]

MACRO_URLS = [
    "https://fred.stlouisfed.org/",
    "https://www.bls.gov/news.release/",
    "https://www.bankofengland.co.uk/",
    "https://www.ecb.europa.eu/",
    "https://www.ons.gov.uk/",
]

GOVERNMENT_URLS = [
    "https://api.usaspending.gov/api/v2/awards/",
    "https://www.sec.gov/edgar/search/",
    "https://www.contractsfinder.service.gov.uk/",
    "https://ted.europa.eu/",
]

SPECIAL_DATASETS = [
    "https://open.fda.gov/",
    "https://www.eia.gov/opendata/",
    "https://www.noaa.gov/",
]

ALL_FINANCE_URLS = list(dict.fromkeys(
    FINANCE_URLS + MACRO_URLS + GOVERNMENT_URLS + SPECIAL_DATASETS
))


# =====================================================================
# LOOKUPS
# =====================================================================

TICKER_MAP = {
    t["ticker"]: t["name"]
    for t in TARGETS
    if t.get("ticker")
}


def detect_targets(text: str) -> list[str]:
    text_lower = text.lower()
    matches = []

    for target in TARGETS:
        for keyword in target["keywords"]:
            if keyword.lower() in text_lower:
                matches.append(target["name"])
                break

    return matches
