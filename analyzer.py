from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from credibility import compute_credibility
from embeddings import generate_embedding
from narrative_engine import engine
from knowledge_graph import build_graph
from target_profiles import detect_targets
from claim_extraction import extract_claims
from knowledge_graph import link_entity_topic
from target_detection import detect_targets
import json

vectorizer = CountVectorizer(stop_words="english", max_features=10)


emotion_words = {
    "joy": ["happy", "great", "good", "love"],
    "anger": ["hate", "angry", "rage"],
    "fear": ["fear", "scared"],
    "sadness": ["sad", "cry"]
}


def extract_keywords(text):

    try:
        X = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()
    except Exception:
        return []


def detect_topics(text):

    words = text.lower().split()

    topic_sets = {
        "technology": ["ai", "software", "data", "cloud"],
        "finance": ["market", "stock", "crypto"],
        "health": ["health", "medicine"]
    }

    topics = []

    for t, keys in topic_sets.items():
        if any(k in words for k in keys):
            topics.append(t)

    return topics


def emotion_analysis(text):

    scores = {k: 0 for k in emotion_words}

    words = text.lower().split()

    for emotion, vocab in emotion_words.items():
        scores[emotion] = sum(1 for w in words if w in vocab)

    return scores


def detect_targets(text):

    matches = []

    lower = text.lower()

    for target in TARGETS:

        for keyword in target["keywords"]:

            if keyword.lower() in lower:

                matches.append(target["name"])
                break

    return matches


def summarize(text):

    sentences = text.split(".")

    return ".".join(sentences[:2])


def analyze(text, url):

    blob = TextBlob(text)

    sentiment = "POSITIVE" if blob.sentiment.polarity > 0 else "NEGATIVE"

    score = blob.sentiment.polarity

    keywords = extract_keywords(text)

    topics = detect_topics(text)

    emotions = emotion_analysis(text)

    summary = summarize(text)

    credibility = compute_credibility(url, text)

    embedding = generate_embedding(summary)

    targets = detect_targets(article_text)

    claims = extract_claims(article_text)

    narrative_id = engine.add_article(text, summary)

    build_graph(topics, keywords)

    return {
        "sentiment": sentiment,
        "score": score,
        "keywords": json.dumps(keywords),
        "topics": json.dumps(topics),
        "summary": summary,
        "emotions": json.dumps(emotions),
        "embedding": json.dumps(embedding),
        "credibility": credibility,
        "narrative_id": narrative_id
    }
