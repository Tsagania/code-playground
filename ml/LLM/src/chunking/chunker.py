"""Chunking strategies for long course book text."""
from __future__ import annotations
import re
from typing import List, Iterable

DEFAULT_CHUNK_SIZE = 800  # approx tokens/words (heuristic)
DEFAULT_CHUNK_OVERLAP = 150

SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")


def naive_word_tokenize(text: str) -> List[str]:
    return re.findall(r"\w+|[^\w\s]", text)


def chunk_by_words(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = end - overlap  # create overlap
    return chunks


def chunk_by_sentences(text: str, max_chars: int = 4000, overlap_sentences: int = 2) -> List[str]:
    sentences = SENTENCE_SPLIT_REGEX.split(text)
    current: List[str] = []
    chunks: List[str] = []
    current_len = 0
    for sent in sentences:
        if current_len + len(sent) > max_chars and current:
            chunks.append(" ".join(current))
            # overlap
            current = current[-overlap_sentences:]
            current_len = sum(len(s) for s in current)
        current.append(sent)
        current_len += len(sent)
    if current:
        chunks.append(" ".join(current))
    return chunks


def adaptive_chunk(text: str, target_tokens: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    # Choose strategy based on length and sentence density
    if len(text) < target_tokens * 1.5:
        return [text]
    avg_sentence_len = sum(len(s) for s in SENTENCE_SPLIT_REGEX.split(text)) / max(1, len(SENTENCE_SPLIT_REGEX.split(text)))
    if avg_sentence_len > 200:  # very long sentences, use word chunking
        return chunk_by_words(text, chunk_size=target_tokens)
    else:
        rough_chars = target_tokens * 5  # heuristic conversion
        return chunk_by_sentences(text, max_chars=rough_chars)


def enumerate_chunks(chunks: Iterable[str], prefix: str = "chunk") -> List[dict]:
    return [{"id": f"{prefix}_{i:06d}", "text": c} for i, c in enumerate(chunks)]


if __name__ == "__main__":
    sample = "This is a sentence. " * 200
    ch = adaptive_chunk(sample)
    for c in ch[:2]:
        print(len(c), c[:80], "...")
