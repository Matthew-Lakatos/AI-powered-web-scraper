from sentence_transformers import SentenceTransformer
import torch
from typing import List
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

_device = "cuda" if torch.cuda.is_available() else "cpu"

model = SentenceTransformer(MODEL_NAME, device=_device)


def _prepare_text(text: str) -> str:
    if not text:
        return ""
    return text[:1000]


def generate_embedding(text: str):

    text = _prepare_text(text)

    if not text:
        return None

    emb = model.encode(text, normalize_embeddings=True)

    return emb.tolist()


def generate_embeddings_batch(texts: List[str]):

    cleaned = [_prepare_text(t) for t in texts]

    embeddings = model.encode(
        cleaned,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    return [e.tolist() for e in embeddings]
