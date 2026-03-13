from typing import Literal, Dict, Any

from transformers import pipeline

# load latest model ( at this time btw )
_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

_sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=_MODEL_NAME,
    tokenizer=_MODEL_NAME
)

SentimentLabel = Literal["NEGATIVE", "NEUTRAL", "POSITIVE"]


def normalize_label(raw_label: str) -> SentimentLabel:
    label = raw_label.upper()
    if "NEG" in label:
        return "NEGATIVE"
    if "NEU" in label:
        return "NEUTRAL"
    if "POS" in label:
        return "POSITIVE"
    # Fallback
    return "NEUTRAL"


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    find sentiment of a given text and return
    """
    if not text or not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}

    result = _sentiment_analyzer(text[:4000])[0] # truncate very long text
    label = normalize_label(result["label"])
    return {"label": label, "score": float(result["score"])}

from typing import Literal, Dict, Any

from transformers import pipeline

from config import settings
from nlp_extra import analyze_full_nlp

_MODEL_NAME = settings.model_sentiment

_sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=_MODEL_NAME,
    tokenizer=_MODEL_NAME
)

SentimentLabel = Literal["NEGATIVE", "NEUTRAL", "POSITIVE"]


def normalize_label(raw_label: str) -> SentimentLabel:
    label = raw_label.upper()
    if "NEG" in label:
        return "NEGATIVE"
    if "NEU" in label:
        return "NEUTRAL"
    if "POS" in label:
        return "POSITIVE"
    return "NEUTRAL"


def analyze_sentiment(text: str) -> Dict[str, Any]:
    if not text or not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}

    result = _sentiment_analyzer(text[:4000])[0]
    label = normalize_label(result["label"])
    return {"label": label, "score": float(result["score"])}


def analyze_all(text: str) -> Dict[str, Any]:
    """
    Full analysis:
    {
      "sentiment": {...},
      "keywords": [...],
      "topics": [...],
      "summary": "...",
      "emotions": {...}
    }
    """
    sentiment = analyze_sentiment(text)
    extras = analyze_full_nlp(text)
    return {
        "sentiment": sentiment,
        **extras,
    }
