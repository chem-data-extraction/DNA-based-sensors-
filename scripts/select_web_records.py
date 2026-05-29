#!/usr/bin/env python3
"""
This script performs ONLY the second-stage record extraction:
- reads data/extracted/web_extracted_candidates.csv produced by extract_web_candidates.py;
- checks that selected expert entries from specs/web_extraction_manifest.json are present in the candidate table;
- downloads the corresponding DNAmoreDB entry pages;
- parses DNAmoreDB fields from the page itself;
- writes data/extracted/web_extracted_records.csv

The script does not use LOD or sensor-performance values. It extracts the DNAmoreDB
fields available on the website 
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

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "specs/web_extraction_manifest.json"
LOG_PATH = ROOT / "data/extracted/extraction_log.jsonl"
IN_CANDIDATES = ROOT / "data/extracted/web_extracted_candidates.csv"
OUT_RECORDS = ROOT / "data/extracted/web_extracted_records.csv"

RECORD_FIELDNAMES = [
    "record_id",
    "candidate_id",
    "source_id",
    "page_id",
    "dnazyme_id",
    "dnazyme_name",
    "selection_reason",
    "reaction",
    "reacting_groups",
    "substrates",
    "product",
    "metal_ion_or_cofactor",
    "linkage",
    "seq_description",
    "buffer_conditions",
    "rate_constant",
    "notes",
    "catalytic_region",
    "reported_publication_year",
    "reported_publication_first_author",
    "reported_publication_lab_or_last_author",
    "reported_publication_title",
    "reported_publication_pmid",
    "reported_publication_doi",
    "reported_publication_url",
    "reported_publication_reaction",
    "source_url",
    "source_location",
    "extraction_method",
    "extraction_confidence"
]

REACTION_TERMS = [
    "RNA cleavage", "RNA ligation", "DNA cleavage", "DNA ligation", "DNA phosphorylation",
    "Porphyrin metalation", "Diels-Alder", "Ester hydrolysis", "Amide hydrolysis",
    "Glycosylation", "Thymine dimer repair", "Reduction", "Reductive amination"
]


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
    text = html.unescape(str(value))
    text = re.sub(r"<\s*sub\s*>\s*([^<]+)\s*<\s*/\s*sub\s*>", r"\1", text, flags=re.I)
    text = re.sub(r"<\s*sup\s*>\s*([^<]+)\s*<\s*/\s*sup\s*>", r"^\1", text, flags=re.I)
    text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def download(url: str, snapshot_path: Path) -> str:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "chem-data-extraction-course/0.5 educational extraction"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    text = response.text
    snapshot_path.write_text(text, encoding="utf-8")
    return text


def lines_from_soup(soup: BeautifulSoup) -> list[str]:
    text = soup.get_text("\n", strip=True)
    return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]


def find_first_line(lines: list[str], pattern: str, start: int = 0) -> tuple[int, str]:
    rx = re.compile(pattern, flags=re.I)
    for i in range(start, len(lines)):
        if rx.search(lines[i]):
            return i, lines[i]
    return -1, ""


def parse_entry_page(
    html_text: str,
    url: str,
    fallback_id: str,
    fallback_name: str,
    candidate_id: str,
    page_id: str,
    source_id: str,
    selection_reason: str
) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    lines = lines_from_soup(soup)
    full_text = "\n".join(lines)

    name = fallback_name
    m = re.search(r"DNAzyme\s+([^\n]+)", full_text)
    if m:
        candidate_name = m.group(1).strip()
        if candidate_name and candidate_name.lower() not in {"description", "name"}:
            name = candidate_name

    reaction = ""
    for term in REACTION_TERMS:
        if term.lower() in full_text.lower():
            reaction = term
            break

    rg_lines = re.findall(r"Group\s+\d+\s+-\s+[^\n]+", full_text)
    reacting_groups = "; ".join(rg_lines)

    substrate_lines = []
    for line in lines:
        if re.match(r"^[XS]:\s", line):
            substrate_lines.append(line)
    substrates = "; ".join(substrate_lines)

    product = ""
    metal = ""
    for line in lines:
        if "specific cleavage" in line.lower():
            if " Mg " in f" {line} " or "Mg 2+" in line:
                product = re.sub(r"\s*Mg\s*2\+.*$", "", line).strip()
                metal = "Mg 2+"
            elif "CEM E. coli" in line:
                product = "specific cleavage at desired position"
                metal = "CEM E. coli"
            elif "TcdC" in line or "TcdC‐24" in line or "TcdC-24" in line:
                product = "specific cleavage at desired position"
                metal = "TcdC-24 protein"
            else:
                product = line.strip()
            break

    linkage = ""
    seq_description = ""
    for line in lines:
        if "RNA phosphodiester" in line:
            linkage = "RNA phosphodiester"
            m_seq = re.search(r"\bN\s*\d+\b", line)
            seq_description = m_seq.group(0).replace(" ", "") if m_seq else ""
            break

    buffer_conditions = ""
    idx, _ = find_first_line(lines, r"^Buffer conditions$")
    if idx >= 0 and idx + 1 < len(lines):
        buffer_conditions = lines[idx + 1]

    rate_constant = ""
    idx, _ = find_first_line(lines, r"k_?\{?cat\}?|k_?\{?obs\}?|kcat|kobs")
    if idx >= 0:
        for j in range(idx, min(idx + 4, len(lines))):
            if re.search(r"k|min\^-?1|h\^-?1|s\^-?1", lines[j], flags=re.I):
                rate_constant = lines[j]
                if j + 1 < len(lines) and re.search(r"min|h|s|cat|obs", lines[j + 1], flags=re.I):
                    rate_constant += " " + lines[j + 1]
                break

    catalytic_region = ""
    idx, _ = find_first_line(lines, r"Catalytic region of the DNAzyme")
    if idx >= 0:
        for j in range(idx + 1, min(idx + 6, len(lines))):
            if re.fullmatch(r"[A-Za-zFRQ\-‐]+", lines[j]) and len(lines[j]) >= 8:
                catalytic_region = lines[j]
                break

    notes = ""
    idx, _ = find_first_line(lines, r"^Notes$")
    if idx >= 0:
        collected = []
        for j in range(idx + 1, len(lines)):
            if re.search(r"Reported in|Related Publications|3D structures|Copyright", lines[j], flags=re.I):
                break
            collected.append(lines[j])
        notes = " ".join(collected).strip()

    pub = {
        "year": "", "first_author": "", "lab_or_last_author": "", "title": "",
        "pmid": "", "doi": "", "reaction": "", "url": ""
    }

    for row in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        if not cells:
            continue
        row_text = " ".join(cells)
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", row_text)
        if doi_match and re.search(r"(19|20)\d{2}", row_text):
            links = row.find_all("a")
            pub["doi"] = doi_match.group(0)
            year_match = re.search(r"(19|20)\d{2}", row_text)
            pub["year"] = year_match.group(0) if year_match else ""
            pmid_match = re.search(r"\b\d{7,9}\b", row_text)
            pub["pmid"] = pmid_match.group(0) if pmid_match else ""
            title_candidates = []
            for a in links:
                at = a.get_text(" ", strip=True)
                href = a.get("href", "")
                if at and not re.fullmatch(r"\d{7,9}", at) and "doi.org" not in href.lower():
                    title_candidates.append(at)
            if title_candidates:
                pub["title"] = title_candidates[0]
                href = links[0].get("href", "") if links else ""
                pub["url"] = urljoin(url, href) if href else ""
            if len(cells) >= 3:
                pub["first_author"] = cells[1]
                pub["lab_or_last_author"] = cells[2]
            pub["reaction"] = reaction
            break

    if not pub["doi"]:
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", full_text)
        pub["doi"] = doi_match.group(0) if doi_match else ""
    if not pub["pmid"]:
        pmid_match = re.search(r"PubMed ID:?\s*(\d{7,9})", full_text, flags=re.I)
        pub["pmid"] = pmid_match.group(1) if pmid_match else ""

    return {
        "record_id": "",
        "candidate_id": candidate_id,
        "source_id": source_id,
        "page_id": page_id,
        "dnazyme_id": fallback_id,
        "dnazyme_name": name,
        "selection_reason": selection_reason,
        "reaction": reaction,
        "reacting_groups": reacting_groups,
        "substrates": substrates,
        "product": product,
        "metal_ion_or_cofactor": metal,
        "linkage": linkage,
        "seq_description": seq_description,
        "buffer_conditions": buffer_conditions,
        "rate_constant": rate_constant,
        "notes": notes,
        "catalytic_region": catalytic_region,
        "reported_publication_year": pub["year"],
        "reported_publication_first_author": pub["first_author"],
        "reported_publication_lab_or_last_author": pub["lab_or_last_author"],
        "reported_publication_title": pub["title"],
        "reported_publication_pmid": pub["pmid"],
        "reported_publication_doi": pub["doi"],
        "reported_publication_url": pub["url"],
        "reported_publication_reaction": pub["reaction"],
        "source_url": url,
        "source_location": "DNAmoreDB entry page",
        "extraction_method": "web_html_entry_page",
        "extraction_confidence": "high"
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def read_candidates() -> pd.DataFrame:
    if not IN_CANDIDATES.exists():
        raise FileNotFoundError(
            f"{IN_CANDIDATES.relative_to(ROOT)} not found. Run scripts/extract_web_candidates.py first."
        )
    return pd.read_csv(IN_CANDIDATES, dtype=str).fillna("")


def main() -> None:
    with MANIFEST.open(encoding="utf-8") as f:
        manifest = json.load(f)

    candidates = read_candidates()
    records: list[dict[str, Any]] = []

    for entry in manifest.get("selected_entry_pages", []):
        selected_id = str(entry.get("dnazyme_id", ""))
        selected_name = str(entry.get("dnazyme_name", ""))
        matches = candidates[(candidates["dnazyme_id"].astype(str) == selected_id) | (candidates["dnazyme_name"].astype(str) == selected_name)]

        if matches.empty:
            append_log({
                "step": "web_record_selection",
                "source_id": entry.get("source_id", ""),
                "page_id": entry.get("page_id", ""),
                "status": "selected_candidate_not_found",
                "tool": "select_web_records.py",
                "output": str(OUT_RECORDS.relative_to(ROOT)),
                "issue": f"Selected entry {selected_id}/{selected_name} was not found in web_extracted_candidates.csv."
            })
            continue

        candidate_row = matches.iloc[0].to_dict()
        candidate_id = candidate_row.get("candidate_id", "")
        source_id = entry["source_id"]
        page_id = entry["page_id"]
        url = entry.get("url") or candidate_row.get("entry_url")
        snapshot_path = ROOT / entry["raw_snapshot_path"]

        try:
            html_text = download(url, snapshot_path)
            row = parse_entry_page(
                html_text=html_text,
                url=url,
                fallback_id=selected_id,
                fallback_name=selected_name,
                candidate_id=candidate_id,
                page_id=page_id,
                source_id=source_id,
                selection_reason=entry.get("selection_reason", "")
            )
            records.append(row)
            append_log({
                "step": "web_record_selection",
                "source_id": source_id,
                "page_id": page_id,
                "status": "ok",
                "tool": "select_web_records.py",
                "candidate_id": candidate_id,
                "raw_snapshot_path": entry["raw_snapshot_path"],
                "records_extracted": 1,
                "output": str(OUT_RECORDS.relative_to(ROOT)),
                "issue": ""
            })
            time.sleep(0.5)
        except Exception as exc:
            append_log({
                "step": "web_record_selection",
                "source_id": source_id,
                "page_id": page_id,
                "status": "failed",
                "tool": "select_web_records.py",
                "candidate_id": candidate_id,
                "output": str(OUT_RECORDS.relative_to(ROOT)),
                "issue": str(exc)
            })

    for i, row in enumerate(records, start=1):
        row["record_id"] = f"web_rec_{i:05d}"

    write_csv(OUT_RECORDS, records, RECORD_FIELDNAMES)

    append_log({
        "step": "web_record_selection",
        "source_id": "selected_web_records",
        "status": "ok",
        "tool": "select_web_records.py",
        "output": str(OUT_RECORDS.relative_to(ROOT)),
        "records_extracted": len(records),
        "issue": "Records were selected from the candidate table and fields were parsed from DNAmoreDB entry pages."
    })

    print(f"Wrote {len(records)} selected DNAmoreDB records to {OUT_RECORDS.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
