from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):

    if not text:
        return None

    emb = model.encode(text)

    return emb.tolist()
