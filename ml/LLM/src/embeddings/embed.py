"""Embedding utilities using sentence-transformers."""
from __future__ import annotations
from pathlib import Path
from typing import List, Sequence
import pickle

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        return np.asarray(self.model.encode(list(texts), batch_size=32, show_progress_bar=True, convert_to_numpy=True))


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity if vectors normalized
    # Normalize for cosine
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index


def save_index(index: faiss.Index, meta: List[dict], index_path: str | Path, meta_path: str | Path) -> None:
    index_path = Path(index_path)
    meta_path = Path(meta_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    with meta_path.open("wb") as f:
        pickle.dump(meta, f)


def load_index(index_path: str | Path, meta_path: str | Path) -> tuple[faiss.Index, List[dict]]:
    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    return index, meta


def search(index: faiss.Index, query_embedding: np.ndarray, top_k: int = 5) -> tuple[np.ndarray, np.ndarray]:
    faiss.normalize_L2(query_embedding)
    distances, idxs = index.search(query_embedding, top_k)
    return distances, idxs


if __name__ == "__main__":  # quick smoke test
    model = EmbeddingModel()
    texts = ["Hello world", "Machine learning course", "Deep learning fundamentals"]
    embs = model.encode(texts)
    idx = build_faiss_index(embs)
    q = model.encode(["What is deep learning?"])
    distances, idxs = search(idx, q, top_k=2)
    for score, i in zip(distances[0], idxs[0]):
        print(score, texts[i])
