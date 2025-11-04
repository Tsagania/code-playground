# Course Book LLM Project

This project lets you build a question-answering system over a 1200-page course PDF. It follows a Retrieval-Augmented Generation (RAG) pipeline with an optional lightweight fine-tuning (LoRA) stage on top of an open-source base model (e.g., `meta-llama/Llama-3-8B-Instruct` or smaller like `mistralai/Mistral-7B-Instruct`).

## Why RAG First, Not Full Training
Training (pretraining) an LLM from scratch on only one book won't be effective (insufficient corpus). Instead:
1. Extract & clean the book text.
2. Chunk it into semantically coherent pieces.
3. Build embeddings + a vector index (FAISS) for fast similarity search.
4. At query time retrieve top-k relevant chunks and feed them into an instruction-tuned model to answer.
5. Optionally apply LoRA fine-tuning with a small set of Q&A pairs derived from the book to improve style and factual grounding.

## High-Level Pipeline
```
PDF -> Raw Text -> Cleaning -> Chunking -> Embeddings -> Vector Index -> Retrieval -> LLM Generation
																							 |                          ^
																							 +----(Optional LoRA fine-tune dataset)----+
```

## Repository Layout (to be created)
```
data/
	raw/                # Original PDF(s)
	processed/          # Extracted & cleaned text
	chunks/             # Serialized chunks (JSONL)
	embeddings/         # FAISS index + metadata
	finetune/           # Q&A pairs for LoRA (JSON / CSV / HF dataset)
src/
	ingest/pdf_loader.py
	preprocessing/cleaning.py
	chunking/chunker.py
	embeddings/embed.py
	vectorstore/store.py
	retrieval/qa.py
	utils/config.py
scripts/
	extract_pdf.py
	build_vector_store.py
	query.py
	finetune_lora.py
	evaluate.py
tests/
	test_pipeline_smoke.py
requirements.txt
README.md
```

## Key Packages
| Purpose                | Package(s) |
|------------------------|------------|
| PDF parsing            | `pypdf` |
| Optional OCR           | `pytesseract`, `Pillow` (if scanned pages) |
| Embeddings             | `sentence-transformers` (e.g., `all-MiniLM-L6-v2`, or domain-specific) |
| Vector index           | `faiss-cpu` |
| LLM + tokenization     | `transformers`, `tiktoken` (if OpenAI style), `accelerate` |
| Parameter-efficient FT | `peft`, `bitsandbytes` (Linux GPU), LoRA adapters |
| Dataset handling       | `datasets` |
| Orchestration (optional)| `langchain` |

Torch install differs by GPU/CPU: see bottom of `requirements.txt`.

## Step-by-Step Workflow
### 1. Environment Setup (Windows PowerShell)
```
python -m venv my-env
my-env\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# Choose torch build (CPU example)
pip install torch==2.3.0+cpu --index-url https://download.pytorch.org/whl/cpu
```

### 2. Place PDF
Put your 1200-page book into `data/raw/course_book.pdf`.

### 3. Extract Text
`extract_pdf.py` will parse pages, optionally OCR images, and write `data/processed/course_book.txt`.

### 4. Clean Text
Removes repeated headers/footers, normalizes whitespace, merges hyphenated line breaks.

### 5. Chunking
Token or sentence-based chunking with overlap to preserve context. Output saved as JSONL (each line: `{id, text}`) in `data/chunks/chunks.jsonl`.

### 6. Embeddings & Index
`build_vector_store.py` loads chunks, computes embeddings, builds FAISS index: `data/embeddings/index.faiss` + metadata `data/embeddings/meta.pkl`.

### 7. Query
Run `query.py --question "Explain the concept of X"` -> retrieves top-k chunks -> composes a prompt -> calls the LLM.

### 8. Optional LoRA Fine-Tune
Curate Q&A pairs from the book (semi-automatic) into `data/finetune/qa.jsonl`. Train LoRA adapters with `finetune_lora.py`. Produces a merged or adapter checkpoint in `outputs/lora/`.

### 9. Evaluation
`evaluate.py` runs a small benchmark of held-out Q&A pairs; computes simple metrics (exact match, Rouge, embedding similarity).

## Configuration
Central parameters (chunk size, overlap, embedding model, index paths) live in `src/utils/config.py`. Override via CLI flags or environment variables.

## Data Formats
1. Chunks JSONL: `{ "id": "chunk_000123", "text": "...", "source_page": 42 }`
2. QA JSONL (fine-tune): `{ "instruction": "Question?", "input": "", "output": "Answer" }` (Alpaca-style)

## Security & Privacy
All processing is local; no remote API calls unless you choose an API model. Keep the book private by avoiding uploads.

## Hardware Considerations
| Model Size | Approx RAM (Inference FP16) | Recommendation |
|------------|-----------------------------|----------------|
| 7-8B       | 16GB GPU (or 32GB CPU slower)| Use quantization (4-bit) |
| 13B        | 24GB GPU                     | Consider smaller model |
| >30B       | 2+ high-memory GPUs          | Not recommended here |

If you lack GPU: rely on smaller models like `Phi-3-mini`, `Llama-3.2-3B`, or run quantized with `bitsandbytes` (Linux) or use `llama.cpp` (separate toolchain).

## Fine-Tuning Strategy (LoRA)
1. Start with ~500 curated Q&A pairs.
2. Train for 3-5 epochs, low learning rate (e.g., 2e-4) with LoRA rank 8.
3. Validate on a held-out set to avoid overfitting factual style.

## Example Prompt Assembly
```
<SYS>You are a helpful course assistant. Use only the provided context.</SYS>
Context:
{{retrieved_chunk_1}}
{{retrieved_chunk_2}}
...
Question: {{user_question}}
Answer:
```

## Next Steps / Enhancements
* Add caching of embeddings.
* Add citation markers referencing page numbers.
* Integrate evaluation with `ragas` library.
* Provide a small web UI (FastAPI + simple frontend).

## Disclaimer
The system retrieves relevant context but may still hallucinate. Always verify important answers against the source pages.

