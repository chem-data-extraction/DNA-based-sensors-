#!/usr/bin/env python3
"""
This script performs only first-pass extraction. It writes automatic candidates to
`data/extracted/pdf_extracted_candidates.csv`; it does not overwrite the manually
verified `data/extracted/pdf_extracted_records.csv`

Manual verification remains required because PDF text extraction can misread tables,
miss paired values, or capture false positives such as absorbance wavelength values
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "specs/pdf_extraction_manifest.json"
OUT_CSV = ROOT / "data/extracted/pdf_extracted_candidates.csv"
LOG_PATH = ROOT / "data/extracted/extraction_log.jsonl"

FIELDNAMES = [
    "candidate_id", "source_id", "pdf_id", "page", "measurement_type",
    "measurement_value", "measurement_unit", "normalized_value_nM",
    "raw_text_snippet", "source_location", "extraction_method",
    "extraction_confidence", "extraction_notes"
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_log(entry: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry.setdefault("timestamp", now_utc())
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def normalize_to_nm(value: float, unit: str) -> str:
    unit_clean = unit.strip().lower().replace("μ", "u").replace("µ", "u")
    if unit_clean == "fm":
        return str(value / 1_000_000.0)
    if unit_clean == "pm":
        return str(value / 1000.0)
    if unit_clean == "nm":
        return str(value)
    if unit_clean == "um":
        return str(value * 1000.0)
    if unit_clean == "m":
        return str(value * 1_000_000_000.0)
    return ""


def extract_text_with_pymupdf(pdf_path: Path, pages_used: list[int]) -> dict[int, str]:
    import fitz  
    page_text: dict[int, str] = {}
    with fitz.open(pdf_path) as doc:
        if not pages_used:
            pages_used = list(range(1, len(doc) + 1))
        for page_num in pages_used:
            idx = page_num - 1
            if 0 <= idx < len(doc):
                page_text[page_num] = doc[idx].get_text("text")
    return page_text


def snippet_around(text: str, start: int, end: int, window: int = 260) -> str:
    return re.sub(r"\s+", " ", text[max(0, start-window): min(len(text), end+window)]).strip()


def is_likely_false_positive(snippet: str, value: float, unit: str) -> bool:
    s = snippet.lower()
    u = unit.lower().replace("μ", "u").replace("µ", "u")
    # Avoid absorbance wavelength: "absorbance at 500 nm"
    if u == "nm" and re.search(r"absorbance\s+(?:of\s+the\s+sensor\s+)?at\s+500\s*nm", s):
        return True
    # Avoid excitation/emission wavelengths
    if u == "nm" and re.search(r"(?:excitation|emission)\s+(?:of|at)\s+\d+\s*nm", s):
        return True
    return False


def add_candidate(rows: list[dict[str, Any]], source_id: str, pdf_id: str, page: int,
                  measurement_type: str, value: float, unit: str, snippet: str,
                  notes: str, confidence: str = "low") -> None:
    if is_likely_false_positive(snippet, value, unit):
        return
    rows.append({
        "candidate_id": f"pdf_cand_{len(rows)+1:05d}",
        "source_id": source_id,
        "pdf_id": pdf_id,
        "page": page,
        "measurement_type": measurement_type,
        "measurement_value": value,
        "measurement_unit": unit,
        "normalized_value_nM": normalize_to_nm(value, unit) if measurement_type == "LOD" else "",
        "raw_text_snippet": snippet,
        "source_location": f"PDF page {page}",
        "extraction_method": "pymupdf_text_regex",
        "extraction_confidence": confidence,
        "extraction_notes": notes,
    })


def find_generic_records(text: str, page: int, source_id: str, pdf_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    units = r"fM|pM|nM|uM|µM|μM|M|ng/μL|ng/uL|ng|pg|fold|%"
    lod_patterns = [
        rf"(?:LOD|LODs|limit of detection|detection limit)[^0-9]{{0,100}}([0-9]+(?:\.[0-9]+)?)\s*({units})",
        rf"([0-9]+(?:\.[0-9]+)?)\s*({units})[^.;]{{0,80}}(?:LOD|LODs|limit of detection|detection limit)",
    ]
    for pat in lod_patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            value = float(m.group(1)); unit = m.group(2)
            snip = snippet_around(text, m.start(), m.end())
            add_candidate(rows, source_id, pdf_id, page, "LOD", value, unit, snip,
                          "Generic LOD candidate; manually verify target, sensor, and condition before final use.")
    for m in re.finditer(r"([0-9]+(?:\.[0-9]+)?)\s*(?:times|fold)\s+(?:lower|less sensitive|improvement)", text, flags=re.IGNORECASE):
        snip = snippet_around(text, m.start(), m.end())
        add_candidate(rows, source_id, pdf_id, page, "sensitivity_improvement_factor", float(m.group(1)), "fold", snip,
                      "Fold-change candidate; manually verify baseline comparator.")
    return rows


def find_solyanikova_pairs(text: str, page: int, source_id: str, pdf_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # 6DNM: HPIV LOD is 10 pM after 1 h and 5 pM after 3 h; RSV LOD is 12 pM after 1 h and 3 pM after 3 h
    pat6 = re.compile(
        r"6DNM[’'`s]*\s+HPIV\s+LOD\s+is\s+([0-9.]+)\s*pM\s+after\s+1\s*h\s+and\s+([0-9.]+)\s*pM\s+after\s+3\s*h\.\s+The\s+6DNM[’'`s]*\s+RSV\s+LOD\s+is\s+([0-9.]+)\s*pM\s+after\s+1\s*h\s+and\s+([0-9.]+)\s*pM\s+after\s+3\s*h",
        flags=re.IGNORECASE)
    for m in pat6.finditer(text):
        snip = snippet_around(text, m.start(), m.end())
        labels = [("HPIV 6DNM 1 h", m.group(1)), ("HPIV 6DNM 3 h", m.group(2)), ("RSV 6DNM 1 h", m.group(3)), ("RSV 6DNM 3 h", m.group(4))]
        for label, val in labels:
            add_candidate(rows, source_id, pdf_id, page, "LOD", float(val), "pM", snip,
                          f"Paired LOD candidate for {label}; manually verify sensor architecture and target type.")
    pat4 = re.compile(
        r"4DNMs[^.]*HPIV\s+detection\s+limits\s+were\s+([0-9.]+)\s*pM\s+after\s+1\s*h\s+and\s+([0-9.]+)\s*pM\s+after\s+3\s*h[^.]*RSVA\s+detection\s+limits\s+were\s+approximately\s+([0-9.]+)\s*pM\s+and\s+([0-9.]+)\s*pM",
        flags=re.IGNORECASE | re.DOTALL)
    for m in pat4.finditer(text):
        snip = snippet_around(text, m.start(), m.end())
        labels = [("HPIV 4DNM 1 h", m.group(1)), ("HPIV 4DNM 3 h", m.group(2)), ("RSVA 4DNM 1 h", m.group(3)), ("RSVA 4DNM 3 h", m.group(4))]
        for label, val in labels:
            add_candidate(rows, source_id, pdf_id, page, "LOD", float(val), "pM", snip,
                          f"Paired 4DNM LOD candidate for {label}; manually verify approximate values.")
    return rows


def main() -> None:
    with MANIFEST.open(encoding="utf-8") as f:
        manifest = json.load(f)
    rows: list[dict[str, Any]] = []
    for src in manifest.get("input_sources", []):
        source_id = src["source_id"]; pdf_id = src["pdf_id"]
        pdf_path = ROOT / src["pdf_path"]
        if not pdf_path.exists():
            append_log({"step": "pdf_extraction", "source_id": source_id, "pdf_id": pdf_id, "status": "missing_pdf", "tool": "extract_pdf.py", "output": str(OUT_CSV.relative_to(ROOT)), "issue": f"Missing {src['pdf_path']}"})
            continue
        try:
            texts = extract_text_with_pymupdf(pdf_path, src.get("pages_used", []))
        except Exception as exc:
            append_log({"step": "pdf_extraction", "source_id": source_id, "pdf_id": pdf_id, "status": "failed", "tool": "extract_pdf.py", "output": str(OUT_CSV.relative_to(ROOT)), "issue": str(exc)})
            continue
        before = len(rows)
        for page, text in texts.items():
            rows.extend(find_generic_records(text, page, source_id, pdf_id))
            if "solyanikova" in source_id:
                rows.extend(find_solyanikova_pairs(text, page, source_id, pdf_id))
        append_log({"step": "pdf_extraction", "source_id": source_id, "pdf_id": pdf_id, "status": "ok", "tool": "extract_pdf.py", "output": str(OUT_CSV.relative_to(ROOT)), "records_extracted": len(rows)-before, "issue": "manual verification required"})
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader(); writer.writerows(rows)
    append_log({"step": "pdf_extraction", "source_id": "all_pdf_sources", "status": "ok", "tool": "extract_pdf.py", "output": str(OUT_CSV.relative_to(ROOT)), "records_extracted": len(rows), "issue": "automatic candidates only; final records are manually curated separately"})
    print(f"Wrote {len(rows)} candidate records to {OUT_CSV.relative_to(ROOT)}")
    print("Manually verified records are kept in data/extracted/pdf_extracted_records.csv")

if __name__ == "__main__":
    main()

