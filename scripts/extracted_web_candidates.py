#!/usr/bin/env python3
"""
This script performs only the first-stage web extraction:
- downloads DNAmoreDB API/HTML sources listed in specs/web_extraction_manifest.json;
- saves raw snapshots under data/raw/web/;
- applies an algorithmic candidate filter;
- writes data/extracted/web_extracted_candidates.csv
"""

from __future__ import annotations

import csv
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "specs/web_extraction_manifest.json"
LOG_PATH = ROOT / "data/extracted/extraction_log.jsonl"
OUT_CANDIDATES = ROOT / "data/extracted/web_extracted_candidates.csv"

CANDIDATE_FIELDNAMES = [
    "candidate_id",
    "source_id",
    "page_id",
    "dnazyme_id",
    "dnazyme_name",
    "reaction",
    "metal_ion_or_cofactor",
    "catalytic_region",
    "substrate_or_sequence_hint",
    "publication_title",
    "publication_year",
    "doi",
    "pmid",
    "measurement_types",
    "measurement_values",
    "measurement_units",
    "measurement_summary",
    "selection_rule",
    "entry_url",
    "source_url",
    "extraction_method",
    "extraction_confidence",
    "raw_text_snippet"
]

NUCLEIC_BACTERIAL_HINTS = [
    "rna", "rrna", "16s", "mrna", "viral rna", "bacterial", "bacteria",
    "e. coli", "escherichia", "clostridium", "c. difficile", "tcdc",
    "nucleic acid", "rna cleavage"
]

SENSOR_HINTS = [
    "sensor", "sensors", "biosensor", "biosensors", "detection", "detect",
    "probe", "probes", "fluorescent", "fluorescence", "fluorogenic",
    "beacon", "reporter", "assay", "indicator", "indicators", "nanomachine"
]

BASE_URL = "https://www.genesilico.pl"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_log(entry: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry.setdefault("timestamp", now_utc())
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    text = html.unescape(str(value))
    text = re.sub(r"<\s*sub\s*>\s*([^<]+)\s*<\s*/\s*sub\s*>", r"\1", text, flags=re.I)
    text = re.sub(r"<\s*sup\s*>\s*([^<]+)\s*<\s*/\s*sup\s*>", r"^\1", text, flags=re.I)
    text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def download(url: str, snapshot_path: Path) -> str:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "chem-data-extraction-course/0.5 educational extraction"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    text = response.text
    snapshot_path.write_text(text, encoding="utf-8")
    return text


def try_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def flatten_json_entries(obj: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def is_entry(d: dict[str, Any]) -> bool:
        keys = {k.lower() for k in d.keys()}
        signals = {"name", "reaction", "metal_ions", "metal_ion", "e", "s", "rate_constant", "yield"}
        return len(keys.intersection(signals)) >= 2

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            if is_entry(x):
                entries.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for item in x:
                walk(item)

    walk(obj)

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for entry in entries:
        key = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique.append(entry)
    return unique


def get_first(entry: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        if key in entry and entry[key] not in (None, ""):
            return clean_text(entry[key])
    return ""


def entry_as_text(entry: dict[str, Any]) -> str:
    return clean_text(json.dumps(entry, ensure_ascii=False))


def infer_selection_rule(entry: dict[str, Any]) -> str:
    text = entry_as_text(entry).lower()
    reaction = get_first(entry, ["reaction"]).lower()
    has_rna_cleavage = "rna cleavage" in reaction or "rna cleavage" in text
    has_nucleic_or_bacterial_hint = any(term in text for term in NUCLEIC_BACTERIAL_HINTS)
    has_sensor_hint = any(term in text for term in SENSOR_HINTS)

    rules: list[str] = []
    if has_rna_cleavage:
        rules.append("reaction_contains_RNA_cleavage")
    if has_nucleic_or_bacterial_hint and has_sensor_hint:
        rules.append("nucleic_or_bacterial_hint_AND_sensor_hint")
    return "; ".join(rules)


def keep_candidate(entry: dict[str, Any]) -> bool:
    return bool(infer_selection_rule(entry))


def parse_measurements_from_entry(entry: dict[str, Any]) -> tuple[str, str, str, str]:
    """Optional candidate metadata only: kcat/kobs/kc/yield when present."""
    measurement_types: list[str] = []
    values: list[str] = []
    units: list[str] = []
    summaries: list[str] = []

    rate_text = get_first(entry, ["rate_constant", "rate", "kinetic_parameter", "kinetic_parameters"])
    if rate_text:
        normalized = rate_text.replace("×", "x")
        pattern = re.compile(
            r"\b(?P<metric>k\s*(?:cat|obs|c)|kcat|kobs|kc)\b\s*=*\s*"
            r"(?P<value>[0-9]+(?:[\.,][0-9]+)?(?:\s*x\s*10\^?-?\d+)?)\s*"
            r"(?P<unit>(?:min|h|hr|s)\s*\^?\s*-?\s*1)",
            flags=re.I,
        )
        for m in pattern.finditer(normalized):
            metric = re.sub(r"\s+", "", m.group("metric").lower())
            value = m.group("value").replace(",", ".")
            unit = m.group("unit").replace(" ", "").replace("hr", "h")
            measurement_types.append(metric)
            values.append(value)
            units.append(unit)
            summaries.append(f"{metric}={value} {unit}")

    yield_text = get_first(entry, ["yield", "yield_percent", "reaction_yield", "product_yield"])
    if yield_text:
        m = re.search(r"([0-9]+(?:[\.,][0-9]+)?(?:\s*[-–—]\s*[0-9]+(?:[\.,][0-9]+)?)?)\s*%?", yield_text)
        if m:
            value = m.group(1).replace(",", ".").replace("–", "-").replace("—", "-")
            measurement_types.append("yield")
            values.append(value)
            units.append("%")
            summaries.append(f"yield={value} %")

    return "; ".join(measurement_types), "; ".join(values), "; ".join(units), "; ".join(summaries)


def parse_publication_fields(entry: dict[str, Any]) -> tuple[str, str, str, str]:
    title = get_first(entry, ["main_article_title", "publication_title", "title"])
    year = get_first(entry, ["main_article_pub_date", "publication_year", "year"])
    year_match = re.search(r"(19|20)\d{2}", year)
    year = year_match.group(0) if year_match else year
    doi = get_first(entry, ["main_article_doi", "doi", "DOI"])
    pmid = get_first(entry, ["main_article_pmid", "pmid", "PMID"])
    raw = json.dumps(entry, ensure_ascii=False)
    if not doi:
        m = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", raw)
        doi = m.group(0) if m else ""
    return title, year, doi, pmid


def get_dnazyme_id(entry: dict[str, Any]) -> str:
    return get_first(entry, ["id", "dnazyme_id", "pk"])


def build_entry_url(entry: dict[str, Any]) -> str:
    entry_id = get_dnazyme_id(entry)
    if entry_id:
        return f"{BASE_URL}/DNAmoreDB/dnazyme/{entry_id}/"
    return ""


def candidates_from_json(text: str, source_id: str, page_id: str, source_url: str) -> list[dict[str, Any]]:
    obj = try_json(text)
    if obj is None:
        return []
    entries = flatten_json_entries(obj)
    rows: list[dict[str, Any]] = []
    for entry in entries:
        if not keep_candidate(entry):
            continue
        title, year, doi, pmid = parse_publication_fields(entry)
        measurement_types, measurement_values, measurement_units, measurement_summary = parse_measurements_from_entry(entry)
        rows.append({
            "candidate_id": "",
            "source_id": source_id,
            "page_id": page_id,
            "dnazyme_id": get_dnazyme_id(entry),
            "dnazyme_name": get_first(entry, ["name", "dnazyme_name"]),
            "reaction": get_first(entry, ["reaction"]),
            "metal_ion_or_cofactor": get_first(entry, ["metal_ions", "metal_ion"]),
            "catalytic_region": get_first(entry, ["e", "catalytic_region"]),
            "substrate_or_sequence_hint": get_first(entry, ["s", "substrates", "substrate"]),
            "publication_title": title,
            "publication_year": year,
            "doi": doi,
            "pmid": pmid,
            "measurement_types": measurement_types,
            "measurement_values": measurement_values,
            "measurement_units": measurement_units,
            "measurement_summary": measurement_summary,
            "selection_rule": infer_selection_rule(entry),
            "entry_url": build_entry_url(entry),
            "source_url": source_url,
            "extraction_method": "api_json",
            "extraction_confidence": "medium",
            "raw_text_snippet": entry_as_text(entry)[:3000],
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def main() -> None:
    with MANIFEST.open(encoding="utf-8") as f:
        manifest = json.load(f)

    candidates: list[dict[str, Any]] = []

    for page in manifest.get("input_pages", []):
        source_id = page["source_id"]
        page_id = page["page_id"]
        url = page["url"]
        snapshot_path = ROOT / page["raw_snapshot_path"]
        try:
            text = download(url, snapshot_path)
            if page.get("page_type") == "api_json" or snapshot_path.suffix.lower() == ".json":
                page_rows = candidates_from_json(text, source_id, page_id, url)
            else:
                page_rows = []
            candidates.extend(page_rows)
            append_log({
                "step": "web_candidate_extraction",
                "source_id": source_id,
                "page_id": page_id,
                "status": "ok",
                "tool": "extract_web_candidates.py",
                "raw_snapshot_path": page["raw_snapshot_path"],
                "candidates_extracted": len(page_rows),
                "output": str(OUT_CANDIDATES.relative_to(ROOT)),
                "issue": ""
            })
            time.sleep(0.5)
        except Exception as exc:
            append_log({
                "step": "web_candidate_extraction",
                "source_id": source_id,
                "page_id": page_id,
                "status": "failed",
                "tool": "extract_web_candidates.py",
                "output": str(OUT_CANDIDATES.relative_to(ROOT)),
                "issue": str(exc)
            })

    seen: set[tuple[str, str, str]] = set()
    unique_candidates: list[dict[str, Any]] = []
    for row in candidates:
        key = (row.get("dnazyme_id", ""), row.get("dnazyme_name", ""), row.get("doi", ""))
        if key in seen:
            continue
        seen.add(key)
        row["candidate_id"] = f"web_cand_{len(unique_candidates) + 1:05d}"
        unique_candidates.append(row)

    write_csv(OUT_CANDIDATES, unique_candidates, CANDIDATE_FIELDNAMES)

    append_log({
        "step": "web_candidate_extraction",
        "source_id": "all_web_candidate_sources",
        "status": "ok",
        "tool": "extract_web_candidates.py",
        "output": str(OUT_CANDIDATES.relative_to(ROOT)),
        "candidates_extracted": len(unique_candidates),
        "issue": "Candidate filter used only algorithmic reaction/context/readout rules, not final selected record names."
    })

    print(f"Wrote {len(unique_candidates)} filtered candidates to {OUT_CANDIDATES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
