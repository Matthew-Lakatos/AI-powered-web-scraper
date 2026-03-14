import faiss
import numpy as np
import pickle
import os
from threading import Lock

INDEX_PATH = "faiss.index"
META_PATH = "faiss_meta.pkl"


class VectorStore:

    def __init__(self, dim=384):

        self.dim = dim
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

        D, I = self.index.search(vec, k)

        results = []

        for idx in I[0]:

            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
