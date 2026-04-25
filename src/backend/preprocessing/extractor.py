from pathlib import Path

from loguru import logger


class ExtractionError(Exception):
    pass


def extract_text(path: Path) -> str:
    path = Path(path)

    if not path.exists():
        raise ExtractionError(f"File not found: {path}")

    # If a .txt file is given directly, read it
    if path.suffix.lower() == ".txt":
        logger.debug(f"Reading txt directly: {path}")
        return path.read_text(encoding="utf-8")

    # Try .txt sidecar alongside the PDF
    txt_sidecar = path.with_suffix(".txt")
    if txt_sidecar.exists():
        logger.debug(f"Using txt sidecar: {txt_sidecar}")
        return txt_sidecar.read_text(encoding="utf-8")

    # Fall back to pdfplumber
    logger.debug(f"Extracting text from PDF: {path}")
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        logger.debug(f"Extracted {len(text)} chars from {len(pages)} pages")
        return text
    except Exception as e:
        raise ExtractionError(f"pdfplumber failed on {path}: {e}") from e
