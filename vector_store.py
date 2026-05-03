import faiss
import numpy as np
import pickle
import os
from threading import Lock
from embeddings import generate_embedding


INDEX_PATH = "faiss.index"
META_PATH  = "faiss_meta.pkl"


class VectorStore:

    def __init__(self, dim=384):

        self.dim  = dim
        self.lock = Lock()

        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        else:
            self.index = faiss.IndexFlatIP(dim)

        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.metadata = []

    def save(self):

        with self.lock:
            faiss.write_index(self.index, INDEX_PATH)

            with open(META_PATH, "wb") as f:
                pickle.dump(self.metadata, f)

    def add(self, embedding, meta):

        if embedding is None:
            return

        with self.lock:
            vec = np.array([embedding]).astype("float32")
            self.index.add(vec)
            self.metadata.append(meta)

    def search(self, embedding, k=5):

        if self.index.ntotal == 0:
            return []

        vec = np.array([embedding]).astype("float32")

        # Clamp k so FAISS never receives a k larger than the index size.
        k = min(k, self.index.ntotal)

        D, I = self.index.search(vec, k)

        results = []

        for score, idx in zip(D[0], I[0]):
            if 0 <= idx < len(self.metadata):
                # Attach similarity score so callers can rank / threshold.
                entry = (
                    dict(self.metadata[idx])
                    if isinstance(self.metadata[idx], dict)
                    else {"data": self.metadata[idx]}
                )
                entry["score"] = round(float(score), 4)
                results.append(entry)

        return results

    def store_embedding(self, text: str, metadata=None):
        """Generate an embedding for *text* and add it to the index.
        """
        vector = generate_embedding(text)
        self.add(vector, metadata)
