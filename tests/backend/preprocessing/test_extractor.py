import pytest
from pathlib import Path

from src.backend.preprocessing.extractor import extract_text, ExtractionError


def test_reads_txt_sidecar(tmp_path: Path):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    txt = tmp_path / "report.txt"
    txt.write_text("Voedselbank tekst inhoud", encoding="utf-8")

    result = extract_text(pdf)
    assert result == "Voedselbank tekst inhoud"


def test_returns_string_not_empty(tmp_path: Path):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    txt = tmp_path / "report.txt"
    txt.write_text("some content", encoding="utf-8")

    result = extract_text(pdf)
    assert isinstance(result, str)
    assert len(result) > 0


def test_raises_on_missing_file(tmp_path: Path):
    missing = tmp_path / "nonexistent.pdf"
    with pytest.raises(ExtractionError, match="not found"):
        extract_text(missing)


def test_accepts_txt_path_directly(tmp_path: Path):
    txt = tmp_path / "report.txt"
    txt.write_text("direct txt content", encoding="utf-8")

    result = extract_text(txt)
    assert result == "direct txt content"
