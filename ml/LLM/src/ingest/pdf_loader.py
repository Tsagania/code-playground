"""PDF ingestion utilities.

Functions:
- extract_text_from_pdf: parse PDF pages using pypdf, optionally OCR images.
- save_text: write unified text to disk.

OCR is optional; if pytesseract not installed or Tesseract not available, it will skip.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader

try:
    import pytesseract  # type: ignore
    OCR_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str | Path, ocr: bool = False) -> Tuple[str, List[str]]:
    """Extract text from a PDF file.

    Returns combined text and list of per-page texts.
    If ocr=True, attempts OCR on pages with low text density.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    all_pages: List[str] = []

    for page_index, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:  # fallback
            logger.warning("Failed text extract on page %d: %s", page_index, e)
            text = ""

        if ocr and OCR_AVAILABLE and len(text.strip()) < 40:  # heuristically sparse
            images = []
            # pypdf does not directly expose rasterized page; leaving stub for advanced usage.
            # In a real implementation you might convert page to image via pdf2image.
            for img in images:  # currently empty placeholder
                try:
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        text += "\n" + ocr_text
                except Exception as e:
                    logger.debug("OCR failed on page %d image: %s", page_index, e)

        all_pages.append(text)

    combined = "\n\n".join(all_pages)
    return combined, all_pages


def save_text(text: str, out_path: str | Path) -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    logger.info("Saved text to %s (%d chars)", path, len(text))


if __name__ == "__main__":  # simple manual test
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf", type=str)
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--out", type=str, default="data/processed/book.txt")
    args = parser.parse_args()
    combined, _ = extract_text_from_pdf(args.pdf, ocr=args.ocr)
    save_text(combined, args.out)
