from typing import List, Dict, Any

from transformers import pipeline
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

from config import settings


# Lazy-loaded globals
_kw_model = None
_topic_classifier = None
_summarizer = None
_emotion_classifier = None


def _get_kw_model():
    global _kw_model
    if _kw_model is None:
        # Lightweight sentence-transformer for KeyBERT
        _kw_model = KeyBERT(SentenceTransformer("all-MiniLM-L6-v2"))
    return _kw_model


def _get_topic_classifier():
    global _topic_classifier
    if _topic_classifier is None:
        _topic_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _topic_classifier


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        _summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )
    return _summarizer


def _get_emotion_classifier():
    global _emotion_classifier
    if _emotion_classifier is None:
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
    return _emotion_classifier


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    if not settings.enable_keywords or not text.strip():
        return []
    model = _get_kw_model()
    keywords = model.extract_keywords(text, top_n=top_n)
    return [kw for kw, score in keywords]


def classify_topics(
    text: str,
    candidate_labels: List[str] = None,
    top_n: int = 3
) -> List[str]:
    if not settings.enable_topics or not text.strip():
        return []

    if candidate_labels is None:
        candidate_labels = [
            "technology",
            "politics",
            "business",
            "science",
            "entertainment",
            "sports",
            "health",
            "education",
            "environment"
        ]

    classifier = _get_topic_classifier()
    result = classifier(text[:1000], candidate_labels)
    labels = result["labels"][:top_n]
    return labels


def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> str:
    if not settings.enable_summarization or not text.strip():
        return ""
    summarizer = _get_summarizer()
    # Truncate input to avoid huge sequences
    input_text = text[:3000]
    summary = summarizer(
        input_text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False
    )[0]["summary_text"]
    return summary


def detect_emotions(text: str) -> Dict[str, float]:
    if not settings.enable_emotions or not text.strip():
        return {}
    classifier = _get_emotion_classifier()
    results = classifier(text[:1000])[0]  # list of {label, score}
    return {item["label"]: float(item["score"]) for item in results}


def analyze_full_nlp(text: str) -> Dict[str, Any]:
    """
    Convenience wrapper: returns all optional NLP features.
    {
      "keywords": [...],
      "topics": [...],
      "summary": "...",
      "emotions": {...}
    }
    """
    return {
        "keywords": extract_keywords(text),
        "topics": classify_topics(text),
        "summary": summarize_text(text),
        "emotions": detect_emotions(text),
    }
