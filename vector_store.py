import faiss
import numpy as np


class VectorStore:

    def __init__(self, dim=384):

        self.index = faiss.IndexFlatL2(dim)

        self.metadata = []

    def add(self, embedding, meta):

        if embedding is None:
            return

        vec = np.array([embedding]).astype("float32")

        self.index.add(vec)

        self.metadata.append(meta)

    def search(self, embedding, k=5):

        vec = np.array([embedding]).astype("float32")

        D, I = self.index.search(vec, k)

        return [self.metadata[i] for i in I[0] if i < len(self.metadata)]
