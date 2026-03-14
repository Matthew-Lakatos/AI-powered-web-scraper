import numpy as np
from embeddings import generate_embedding
import time
import math


SIM_THRESHOLD = 0.82


class NarrativeEngine:

    def __init__(self):
        self.clusters = []

    def _similarity(self, a, b):

        a = np.array(a)
        b = np.array(b)

        return float(np.dot(a, b))

    def recency_weight(timestamp):

        age_days = (time.time() - timestamp) / 86400
    
        return math.exp(-0.05 * age_days)


    def narrative_importance(cluster):
    
        credibility = cluster.get("credibility", 0.5)
    
        timestamp = cluster.get("timestamp", time.time())
    
        size = cluster.get("size", 1)
    
        return credibility * recency_weight(timestamp) * size

    def add_article(self, text, summary):

        emb = generate_embedding(summary or text[:500])

        if emb is None:
            return None

        for cluster in self.clusters:

            sim = self._similarity(emb, cluster["centroid"])

            if sim > SIM_THRESHOLD:

                cluster["articles"].append(summary)

                cluster["centroid"] = (
                    (np.array(cluster["centroid"]) + np.array(emb)) / 2
                ).tolist()

                return cluster["id"]

        cid = len(self.clusters)

        self.clusters.append({
            "id": cid,
            "centroid": emb,
            "articles": [summary]
        })

        return cid


engine = NarrativeEngine()
