from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

BASE_EXPANSIONS = [
    "policy",
    "economics",
    "ethics",
    "industry impact",
    "research",
    "controversy",
    "debate",
    "future outlook"
]


def expand_topic(topic):

    expansions = []

    for base in BASE_EXPANSIONS:

        expansions.append(f"{topic} {base}")

    expansions.append(topic)

    return list(set(expansions))
