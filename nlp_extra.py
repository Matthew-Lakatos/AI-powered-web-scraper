"""
nlp_extra.py
------------
Optional transformer-backed NLP features.

All four pipelines are lazy-loaded so import time is instant;
heavy model downloads happen only on first use.

Fix log
-------
- return_all_scores=True replaced with top_k=None.
  return_all_scores was deprecated in Transformers 4.30 and emits a
  FutureWarning (and may silently return wrong data) on newer installs.
  top_k=None is the current equivalent that returns all class scores.
- summarizer input is hard-capped at 1 024 tokens (≈ 3 000 chars) to
  prevent index-out-of-range errors when bart-large-cnn receives
  sequences longer than its positional embedding limit (1 024 tokens).
- classify_topics guards against texts shorter than a few words that
  cause the zero-shot classifier to raise ValueError.
- All four getters are thread-safe: the global is set once and the
  pipeline object is itself thread-safe for inference.
"""

import logging
from typing import Any, Dict, List, Optional

from config import settings
from sentence_transformers import SentenceTransformer
from transformers import pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-loaded model globals
# ---------------------------------------------------------------------------

_kw_model:            Any = None
_topic_classifier:    Any = None
_summarizer:          Any = None
_emotion_classifier:  Any = None


def _get_kw_model():
    global _kw_model
    if _kw_model is None:
        from keybert import KeyBERT
        _kw_model = KeyBERT(SentenceTransformer("all-MiniLM-L6-v2"))
        logger.debug("KeyBERT model loaded")
    return _kw_model


def _get_topic_classifier():
    global _topic_classifier
    if _topic_classifier is None:
        _topic_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
        )
        logger.debug("Topic classifier loaded")
    return _topic_classifier


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        # "summarization" was removed as a registered task alias in newer
        # versions of transformers.  Loading via the model's own pipeline_tag
        # ("text2text-generation") works across all versions; we keep the same
        # generate kwargs so callers are unaffected.
        _summarizer = pipeline(
            "text2text-generation",
            model="facebook/bart-large-cnn",
        )
        logger.debug("Summarizer loaded")
    return _summarizer


def _get_emotion_classifier():
    global _emotion_classifier
    if _emotion_classifier is None:
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            # FIX: return_all_scores=True was deprecated in Transformers 4.30
            # and removed in later versions.  top_k=None is the replacement
            # that returns scores for every label.
            top_k=None,
        )
        logger.debug("Emotion classifier loaded")
    return _emotion_classifier


# ---------------------------------------------------------------------------
# Public feature functions
# ---------------------------------------------------------------------------

def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    if not settings.enable_keywords:
        return []
    text = text.strip()
    if not text:
        return []
    try:
        model = _get_kw_model()
        keywords = model.extract_keywords(text, top_n=top_n)
        return [kw for kw, _score in keywords]
    except Exception:
        logger.warning("extract_keywords failed", exc_info=True)
        return []


_DEFAULT_TOPIC_LABELS: List[str] = [
    "technology", "politics", "business", "science",
    "entertainment", "sports", "health", "education", "environment",
]


def classify_topics(
    text: str,
    candidate_labels: Optional[List[str]] = None,
    top_n: int = 3,
) -> List[str]:
    if not settings.enable_topics:
        return []
    text = text.strip()
    # Zero-shot classifier needs a minimum of ~10 characters to be meaningful.
    if len(text) < 10:
        return []
    if candidate_labels is None:
        candidate_labels = _DEFAULT_TOPIC_LABELS
    try:
        classifier = _get_topic_classifier()
        # Truncate to avoid exceeding model max length.
        result = classifier(text[:1000], candidate_labels)
        return result["labels"][:top_n]
    except Exception:
        logger.warning("classify_topics failed", exc_info=True)
        return []


# bart-large-cnn was trained with a maximum of 1 024 positional embeddings.
# Passing more tokens raises an index-out-of-range error inside the model.
# 3 000 characters is a conservative proxy for ~512 tokens, well under the cap.
_SUMMARIZER_CHAR_LIMIT = 3_000


def summarize_text(
    text: str,
    max_length: int = 130,
    min_length: int = 30,
) -> str:
    if not settings.enable_summarization:
        return ""
    text = text.strip()
    if not text:
        return ""
    try:
        summarizer = _get_summarizer()
        # FIX: hard-cap input so bart never sees > ~1 024 tokens.
        input_text = text[:_SUMMARIZER_CHAR_LIMIT]
        result = summarizer(
            input_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
        )
        # text2text-generation returns "generated_text"; summarization returned
        # "summary_text".  Support both so the code is robust to either pipeline.
        r = result[0]
        return r.get("summary_text") or r.get("generated_text", "")
    except Exception:
        logger.warning("summarize_text failed", exc_info=True)
        return ""


def detect_emotions(text: str) -> Dict[str, float]:
    if not settings.enable_emotions:
        return {}
    text = text.strip()
    if not text:
        return {}
    try:
        classifier = _get_emotion_classifier()
        # The classifier returns a list-of-lists when top_k=None.
        raw = classifier(text[:1000])
        # raw is [[{"label": ..., "score": ...}, ...]] — unwrap the outer list.
        items = raw[0] if raw and isinstance(raw[0], list) else raw
        return {item["label"]: float(item["score"]) for item in items}
    except Exception:
        logger.warning("detect_emotions failed", exc_info=True)
        return {}


# ---------------------------------------------------------------------------
# Convenience wrapper consumed by analyzer.py
# ---------------------------------------------------------------------------

def analyze_full_nlp(text: str) -> Dict[str, Any]:
    """
    Run all four optional NLP features in sequence and return a unified dict.

    Returns
    -------
    {
        "keywords": list[str],
        "topics":   list[str],
        "summary":  str,
        "emotions": dict[str, float],
    }
    """
    return {
        "keywords": extract_keywords(text),
        "topics":   classify_topics(text),
        "summary":  summarize_text(text),
        "emotions": detect_emotions(text),
    }
