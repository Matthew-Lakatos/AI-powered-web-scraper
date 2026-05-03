"""
analyzer.py
-----------
Central NLP analysis module.

Public API
----------
analyze_all(text, url='') -> dict
    Returns a fully structured analysis dict consumed by main.py,
    auto_explorer.py, and the API layer.

    Keys:
        sentiment  : {"label": str, "score": float}
        keywords   : list[str]
        topics     : list[str]
        summary    : str
        emotions   : dict[str, float | int]
        propaganda : {"score": float, "flags": list[str],
                      "confidence": str, "techniques": list[dict]}

Internal helpers are kept private (prefixed with _).
"""

import logging
from typing import Any

from textblob import TextBlob

# NLP helpers — lazy-loaded heavy models live in nlp_extra
from nlp_extra import analyze_full_nlp

# Post-analysis enrichment
from credibility import compute_credibility
from embeddings import generate_embedding
from narrative_engine import engine
from knowledge_graph import link_entity_topic
from target_profiles import detect_targets       # single, correct import
from claim_extraction import extract_claims
from propaganda_detector import detect_propaganda

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lightweight fallbacks (used when nlp_extra models are disabled / unavailable)
# ---------------------------------------------------------------------------

def _fallback_keywords(text: str) -> list[str]:
    """
    Simple bag-of-words keyword extractor used when KeyBERT is disabled.
    Returns up to 10 content words ranked by frequency.
    """
    from sklearn.feature_extraction.text import CountVectorizer
    try:
        vec = CountVectorizer(stop_words="english", max_features=10)
        vec.fit_transform([text])
        return vec.get_feature_names_out().tolist()
    except Exception:
        return []


_TOPIC_SETS: dict[str, list[str]] = {
    "technology": ["ai", "software", "data", "cloud", "algorithm"],
    "finance":    ["market", "stock", "crypto", "bank", "economy"],
    "health":     ["health", "medicine", "vaccine", "disease", "treatment"],
    "politics":   ["government", "election", "policy", "senate", "congress"],
    "science":    ["research", "study", "experiment", "discovery"],
}


def _fallback_topics(text: str) -> list[str]:
    words = set(text.lower().split())
    return [t for t, keys in _TOPIC_SETS.items() if any(k in words for k in keys)]


_EMOTION_VOCAB: dict[str, list[str]] = {
    "joy":     ["happy", "great", "good", "love", "excellent", "wonderful"],
    "anger":   ["hate", "angry", "rage", "furious", "outraged"],
    "fear":    ["fear", "scared", "terrified", "anxious", "worried"],
    "sadness": ["sad", "cry", "depressed", "grief", "sorrow"],
}


def _fallback_emotions(text: str) -> dict[str, int]:
    words = text.lower().split()
    return {
        emotion: sum(1 for w in words if w in vocab)
        for emotion, vocab in _EMOTION_VOCAB.items()
    }


def _fallback_summary(text: str) -> str:
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return ". ".join(sentences[:2]) + ("." if sentences else "")


# ---------------------------------------------------------------------------
# Sentiment (TextBlob — always available, no heavy model needed)
# ---------------------------------------------------------------------------

def _sentiment(text: str) -> dict[str, Any]:
    blob = TextBlob(text)
    polarity: float = blob.sentiment.polarity
    label = "POSITIVE" if polarity > 0 else ("NEGATIVE" if polarity < 0 else "NEUTRAL")
    return {"label": label, "score": round(polarity, 4)}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_all(text: str, url: str = "") -> dict[str, Any]:
    """
    Run the full NLP pipeline on *text*.

    Parameters
    ----------
    text : str
        Raw page text extracted by the scraper.
    url  : str
        Source URL — used for credibility scoring and knowledge graph links.

    Returns
    -------
    dict with keys:
        sentiment, keywords, topics, summary, emotions, propaganda,
        credibility, targets, claims, narrative_id
    """
    if not text:
        return _empty_result()

    # 1. Sentiment — fast, always runs
    sentiment = _sentiment(text)

    # 2. Rich NLP via nlp_extra (transformer models, lazy-loaded)
    #    Falls back gracefully if models are disabled in settings.
    try:
        rich = analyze_full_nlp(text)
        keywords: list[str] = rich["keywords"] or _fallback_keywords(text)
        topics:   list[str] = rich["topics"]   or _fallback_topics(text)
        summary:  str       = rich["summary"]  or _fallback_summary(text)
        emotions: dict      = rich["emotions"] or _fallback_emotions(text)
    except Exception:
        logger.warning("nlp_extra failed — using lightweight fallbacks", exc_info=True)
        keywords = _fallback_keywords(text)
        topics   = _fallback_topics(text)
        summary  = _fallback_summary(text)
        emotions = _fallback_emotions(text)

    # 3. Propaganda detection (pure-Python lexicon, always runs)
    prop_result = detect_propaganda(text)
    propaganda = {
        "score":      prop_result["score"],
        "flags":      prop_result["flags"],
        "confidence": prop_result["confidence"],
        "techniques": prop_result["techniques"],
    }

    # 4. Credibility (URL + content heuristics, always runs)
    credibility: float = compute_credibility(url, text) if url else 0.5

    # 5. Target entity detection
    targets: list[str] = detect_targets(text)

    # 6. Claim extraction (OpenAI-backed, may return None if key absent)
    claims = extract_claims(text)

    # 7. Narrative clustering (embedding-based, in-memory)
    narrative_id = None
    try:
        narrative_id = engine.add_article(text, summary)
    except Exception:
        logger.warning("Narrative engine failed", exc_info=True)

    # 8. Knowledge graph links
    for target in targets:
        for topic in topics:
            try:
                link_entity_topic(target, topic)
            except Exception:
                pass

    return {
        "sentiment":    sentiment,      # {"label": str, "score": float}
        "keywords":     keywords,       # list[str]
        "topics":       topics,         # list[str]
        "summary":      summary,        # str
        "emotions":     emotions,       # dict[str, float|int]
        "propaganda":   propaganda,     # {"score", "flags", "confidence", "techniques"}
        "credibility":  credibility,    # float  [0.0–1.0]
        "targets":      targets,        # list[str]
        "claims":       claims,         # str | None
        "narrative_id": narrative_id,  # int | None
    }


def _empty_result() -> dict[str, Any]:
    """Returned when the input text is empty."""
    return {
        "sentiment":    {"label": "NEUTRAL", "score": 0.0},
        "keywords":     [],
        "topics":       [],
        "summary":      "",
        "emotions":     {},
        "propaganda":   {"score": 0.0, "flags": [], "confidence": "clean", "techniques": []},
        "credibility":  0.5,
        "targets":      [],
        "claims":       None,
        "narrative_id": None,
    }
