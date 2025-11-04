"""Vector store abstraction over FAISS index."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict

import faiss

from src.embeddings.embed import EmbeddingModel, build_faiss_index, save_index, load_index, search


class VectorStore:
    def __init__(self, embedding_model: EmbeddingModel, index_path: str | Path, meta_path: str | Path):
        self.embedding_model = embedding_model
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.index: faiss.Index | None = None
        self.meta: List[Dict] | None = None

    def build(self, chunks: List[Dict]) -> None:
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_model.encode(texts)
        idx = build_faiss_index(embeddings)
        save_index(idx, chunks, self.index_path, self.meta_path)
        self.index = idx
        self.meta = chunks

    def load(self) -> None:
        self.index, self.meta = load_index(self.index_path, self.meta_path)

    def query(self, question: str, top_k: int = 5) -> List[Dict]:
        if self.index is None or self.meta is None:
            raise RuntimeError("Index not loaded")
        q_emb = self.embedding_model.encode([question])
        distances, idxs = search(self.index, q_emb, top_k=top_k)
        results = []
        for score, i in zip(distances[0], idxs[0]):
            chunk = self.meta[int(i)]
            results.append({"score": float(score), **chunk})
        return results


if __name__ == "__main__":  # smoke test
    model = EmbeddingModel()
    sample_chunks = [{"id": "c1", "text": "Neural networks learn representations."}, {"id": "c2", "text": "Support vector machines are margin-based classifiers."}]
    vs = VectorStore(model, "data/embeddings/index.faiss", "data/embeddings/meta.pkl")
    vs.build(sample_chunks)
    vs.load()
    print(vs.query("What are classifiers?"))
