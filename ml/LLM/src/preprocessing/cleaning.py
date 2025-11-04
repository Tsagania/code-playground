"""Text cleaning utilities for course book."""
from __future__ import annotations
import re
from typing import Iterable

HEADER_FOOTER_PATTERN = re.compile(r"^(?:Chapter\s+\d+|Page\s+\d+|\d+)$", re.IGNORECASE)
MULTISPACE_PATTERN = re.compile(r"[ \t]{2,}")
HYPHEN_LINEBREAK_PATTERN = re.compile(r"(\w+)-\n(\w+)")


def remove_headers_and_footers(lines: Iterable[str]) -> list[str]:
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if HEADER_FOOTER_PATTERN.match(stripped):
            continue
        cleaned.append(stripped)
    return cleaned


def merge_hyphenated(text: str) -> str:
    return HYPHEN_LINEBREAK_PATTERN.sub(lambda m: m.group(1) + m.group(2), text)


def normalize_whitespace(text: str) -> str:
    # Collapse multiple spaces, standardize newlines
    text = MULTISPACE_PATTERN.sub(" ", text)
    text = re.sub(r"\r\n?", "\n", text)
    return text


def clean_text(raw: str) -> str:
    lines = raw.splitlines()
    lines = remove_headers_and_footers(lines)
    merged = "\n".join(lines)
    merged = merge_hyphenated(merged)
    merged = normalize_whitespace(merged)
    return merged.strip()


if __name__ == "__main__":  # quick test
    sample = """Chapter 1\nIntroduction to AI\nPage 12\nThis is an ex-\nample   sentence."""
    print(clean_text(sample))
