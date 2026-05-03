"""
config.py — centralised settings loaded from environment variables.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def _bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

def _int(key: str, default: int) -> int:
    try:
        return int(os.environ[key])
    except (KeyError, ValueError):
        return default

def _str(key: str, default: str = "") -> str:
    return os.getenv(key, default)

def _optional(key: str) -> Optional[str]:
    v = os.getenv(key, "").strip()
    return v if v else None

@dataclass
class Settings:
    # PostgreSQL / TimescaleDB
    postgres_dsn: str = field(default_factory=lambda: _str("POSTGRES_DSN", "postgresql://scraper:scraper@localhost:5432/scraper"))
    db_pool_min: int = field(default_factory=lambda: _int("DB_POOL_MIN", 5))
    db_pool_max: int = field(default_factory=lambda: _int("DB_POOL_MAX", 20))
    # Scraping
    concurrency_limit: int = field(default_factory=lambda: _int("CONCURRENCY_LIMIT", 20))
    scrape_retries: int = field(default_factory=lambda: _int("SCRAPE_RETRIES", 5))
    scrape_timeout_connect: float = field(default_factory=lambda: float(_str("SCRAPE_TIMEOUT_CONNECT", "5")))
    scrape_timeout_read: float = field(default_factory=lambda: float(_str("SCRAPE_TIMEOUT_READ", "20")))
    scrape_max_response_bytes: int = field(default_factory=lambda: _int("SCRAPE_MAX_RESPONSE_BYTES", 5_242_880))
    enable_selenium_fallback: bool = field(default_factory=lambda: _bool("ENABLE_SELENIUM_FALLBACK", True))
    chromedriver_path: str = field(default_factory=lambda: _str("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver"))
    # robots.txt / politeness
    robots_default_delay: float = field(default_factory=lambda: float(_str("ROBOTS_DEFAULT_DELAY", "1.0")))
    dead_source_threshold: int = field(default_factory=lambda: _int("DEAD_SOURCE_THRESHOLD", 5))
    dead_source_recheck_hours: int = field(default_factory=lambda: _int("DEAD_SOURCE_RECHECK_HOURS", 24))
    # NLP models
    model_sentiment: str = field(default_factory=lambda: _str("MODEL_SENTIMENT", "ProsusAI/finbert"))
    model_embedding: str = field(default_factory=lambda: _str("MODEL_EMBEDDING", "all-MiniLM-L6-v2"))
    model_embedding_dim: int = field(default_factory=lambda: _int("MODEL_EMBEDDING_DIM", 384))
    model_embedding_version: str = field(default_factory=lambda: _str("MODEL_EMBEDDING_VERSION", "all-MiniLM-L6-v2-v1"))
    enable_keywords: bool = field(default_factory=lambda: _bool("ENABLE_KEYWORDS", True))
    enable_topics: bool = field(default_factory=lambda: _bool("ENABLE_TOPICS", True))
    enable_summarization: bool = field(default_factory=lambda: _bool("ENABLE_SUMMARIZATION", True))
    enable_emotions: bool = field(default_factory=lambda: _bool("ENABLE_EMOTIONS", True))
    sentiment_confidence_threshold: float = field(default_factory=lambda: float(_str("SENTIMENT_CONFIDENCE_THRESHOLD", "0.55")))
    # Deduplication
    dedup_similarity_threshold: float = field(default_factory=lambda: float(_str("DEDUP_SIMILARITY_THRESHOLD", "0.92")))
    dedup_lookback_hours: int = field(default_factory=lambda: _int("DEDUP_LOOKBACK_HOURS", 48))
    # Materiality
    materiality_min_alert_tier: str = field(default_factory=lambda: _str("MATERIALITY_MIN_ALERT_TIER", "MEDIUM"))
    # Caching / scheduling
    cache_expiry_hours: int = field(default_factory=lambda: _int("CACHE_EXPIRY_HOURS", 24))
    pipeline_interval_seconds: int = field(default_factory=lambda: _int("PIPELINE_INTERVAL_SECONDS", 3600))
    # Alerts
    alert_webhook_url: Optional[str] = field(default_factory=lambda: _optional("ALERT_WEBHOOK_URL"))
    alert_smtp_host: Optional[str] = field(default_factory=lambda: _optional("ALERT_SMTP_HOST"))
    alert_smtp_port: int = field(default_factory=lambda: _int("ALERT_SMTP_PORT", 465))
    alert_smtp_user: Optional[str] = field(default_factory=lambda: _optional("ALERT_SMTP_USER"))
    alert_smtp_password: Optional[str] = field(default_factory=lambda: _optional("ALERT_SMTP_PASSWORD"))
    alert_smtp_from: Optional[str] = field(default_factory=lambda: _optional("ALERT_SMTP_FROM"))
    alert_smtp_to: Optional[str] = field(default_factory=lambda: _optional("ALERT_SMTP_TO"))
    # API
    api_host: str = field(default_factory=lambda: _str("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: _int("API_PORT", 8000))
    api_key: str = field(default_factory=lambda: _str("API_KEY", "change-me-in-production"))
    api_rate_limit_per_minute: int = field(default_factory=lambda: _int("API_RATE_LIMIT_PER_MINUTE", 60))
    dashboard_port: int = field(default_factory=lambda: _int("DASHBOARD_PORT", 8501))
    # Observability
    prometheus_port: int = field(default_factory=lambda: _int("PROMETHEUS_PORT", 9090))
    log_level: str = field(default_factory=lambda: _str("LOG_LEVEL", "INFO").upper())
    log_format: str = field(default_factory=lambda: _str("LOG_FORMAT", "json"))

settings = Settings()
