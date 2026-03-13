import os
from dataclasses improt dataclass
from dotenv import load_dotenv

load_dotenv()

def _get_bool(value: str, default: bool = False) -> bool:
  if value is None:
    return default
  return value.strip().lower() in ("1", "true", "yes", "on")

def _get_int(value: str, default: int) -> int:
  try:
    return int(value)
  except:
    return default

@dataclass
class Settings:
  # core system
  chromedriver_path: str
  database_path: str
  concurrency_limit: int
  enable_selenium_fallback: bool
  enable_emotions: bool
  log_level: str

  # nlp models
  model_sentiment: str
  enable_keywords: bool
  enable_topics: bool
  enable_summarization: bool
  enable_emotions: bool

  # caching for efficiency
  cache_expiry_hours: int

  # dashboard/API
  api_host: str
  api_port: int
  dashboard_port: int

def load_settings() -> Settings:
    return Settings(
        # Core system
        chromedriver_path=os.getenv("CHROMEDRIVER_PATH", ""),
        database_path=os.getenv("DATABASE_PATH", "scraped_data.db"),
        concurrency_limit=_get_int(os.getenv("CONCURRENCY_LIMIT"), 10),
        enable_selenium_fallback=_get_bool(os.getenv("ENABLE_SELENIUM_FALLBACK"), True),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),

        # NLP models
        model_sentiment=os.getenv(
            "MODEL_SENTIMENT",
            "cardiffnlp/twitter-roberta-base-sentiment-latest"
        ),
        enable_keywords=_get_bool(os.getenv("ENABLE_KEYWORDS"), True),
        enable_topics=_get_bool(os.getenv("ENABLE_TOPICS"), True),
        enable_summarization=_get_bool(os.getenv("ENABLE_SUMMARIZATION"), True),
        enable_emotions=_get_bool(os.getenv("ENABLE_EMOTIONS"), True),

        # Caching
        cache_expiry_hours=_get_int(os.getenv("CACHE_EXPIRY_HOURS"), 24),

        # Dashboard / API
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=_get_int(os.getenv("API_PORT"), 8000),
        dashboard_port=_get_int(os.getenv("DASHBOARD_PORT"), 8501),
    )


# Create a global settings object
settings = load_settings()
