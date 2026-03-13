from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
import json

vectorizer = CountVectorizer(stop_words="english", max_features=10)

emotion_words = {
    "joy": ["happy", "great", "good", "love"],
    "anger": ["hate", "angry", "rage"],
    "fear": ["fear", "scared", "terrified"],
    "sadness": ["sad", "depressed", "cry"]
}


def extract_keywords(text):

    try:
        X = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()
    except Exception:
        return []


def detect_topics(text):

    words = text.lower().split()

    topics = []

    topic_sets = {
        "technology": ["ai", "software", "data", "cloud", "python"],
        "finance": ["market", "stock", "crypto", "money"],
        "health": ["health", "medicine", "doctor", "fitness"]
    }

    for topic, keys in topic_sets.items():
        if any(k in words for k in keys):
            topics.append(topic)

    return topics


def emotion_analysis(text):

    scores = {k: 0 for k in emotion_words}

    words = text.lower().split()

    for emotion, vocab in emotion_words.items():
        scores[emotion] = sum(1 for w in words if w in vocab)

    return scores


def summarize(text):

    sentences = text.split(".")
    return ".".join(sentences[:2])


def analyze(text):
    """
    Legacy simple analysis (kept for compatibility)
    """

    blob = TextBlob(text)

    sentiment = "POSITIVE" if blob.sentiment.polarity > 0 else "NEGATIVE"

    score = blob.sentiment.polarity

    keywords = extract_keywords(text)

    topics = detect_topics(text)

    emotions = emotion_analysis(text)

    summary = summarize(text)

    return {
        "sentiment": sentiment,
        "score": score,
        "keywords": json.dumps(keywords),
        "topics": json.dumps(topics),
        "emotions": json.dumps(emotions),
        "summary": summary
    }


def analyze_all(text):
    """
    Full analysis used by main pipeline.
    This restores functionality expected by main.py
    """

    blob = TextBlob(text)

    sentiment_score = blob.sentiment.polarity
    sentiment_label = "POSITIVE" if sentiment_score > 0 else "NEGATIVE"

    keywords = extract_keywords(text)
    topics = detect_topics(text)
    emotions = emotion_analysis(text)
    summary = summarize(text)

    return {
        "sentiment": {
            "label": sentiment_label,
            "score": sentiment_score
        },
        "keywords": keywords,
        "topics": topics,
        "summary": summary,
        "emotions": emotions
    }

