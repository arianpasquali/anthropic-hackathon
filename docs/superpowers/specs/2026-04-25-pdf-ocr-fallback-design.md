# PDF OCR Fallback via Anthropic Document API

**Date:** 2026-04-25  
**Status:** Approved

## Problem

Some PDFs yield sparse or empty text — either because a `.txt` sidecar is near-empty, or because `pdfplumber` fails to extract meaningful text from scanned/image-only PDFs. When `_call_claude` receives fewer than ~500 chars it skips the API call and returns empty extraction results.

## Approach

Use the Anthropic Messages API's native PDF document support. When extracted text is below the threshold, pass the raw PDF bytes as a `base64` document content block. Claude handles both text-layer extraction and OCR internally.

## Threshold

`MIN_TEXT_CHARS = 500` in `extractor.py`.  
Condition: `len(text.strip()) < MIN_TEXT_CHARS` → PDF fallback.

## Changes

### `extractor.py`
- Add `MIN_TEXT_CHARS = 500` constant.
- No change to `extract_text` — it still returns whatever text it can (pdfplumber or sidecar).

### `claude.py`
- Add `_call_claude_pdf(client, pdf_path, tool_name, model, source_label)`:
  - Reads PDF bytes, base64-encodes them.
  - Sends as `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}}` content block.
  - Same retry logic and drift detection as `_call_claude`.
- Modify `extract_all(text, model, source_label, pdf_path=None)`:
  - If `text` is sparse (`len(text.strip()) < MIN_TEXT_CHARS`) and `pdf_path` is provided, dispatch `_call_claude_pdf` for all 5 parallel tools.
  - Otherwise dispatch `_call_claude` as today.

### `cli.py`
- In `ingest` and `ingest_dir`: after `extract_text`, check threshold.
- If sparse and source file is a PDF, pass `pdf_path=file` into `extract_all`.
- Log: `"sparse text ({n} chars) — falling back to PDF document API"`.
- `save_text` sidecar behaviour unchanged.

## Scope Boundaries

- `openai_compat.py` (orq provider): no change. If provider is `orq` and text is sparse, log a warning and proceed with sparse text.
- `regex_extract.py`: no change — runs on text as before; on sparse text it simply finds nothing.

## Constraints

- Anthropic PDF document API: max 32 MB, 100 pages per document.
- Each fallback ingestion sends the full PDF 5× (one per extraction tool). Acceptable for offline batch pipeline.
