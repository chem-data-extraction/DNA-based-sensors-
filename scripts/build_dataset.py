#!/usr/bin/env python3
"""Build interim dataset by merging PDF and web extracted records

This script does only merging and source-specific schema mapping
Cleaning, normalization, and deduplication are handled by scripts/clean_dataset.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF_CSV = ROOT / "data/extracted/pdf_extracted_records.csv"
WEB_CSV = ROOT / "data/extracted/web_extracted_records.csv"
SCHEMA_PATH = ROOT / "specs/dataset_schema.json"
MERGED_PATH = ROOT / "data/interim/merged_records.csv"


def load_schema_columns() -> list[str]:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    return [field["name"] for field in schema["fields"]]


def text(row: pd.Series, key: str, default: str = "") -> str:
    value = row.get(key, default)
    if pd.isna(value):
        return default
    return str(value)


def value(row: pd.Series, key: str):
    value = row.get(key, None)
    if pd.isna(value):
        return None
    return value


def infer_target_type(target_name: str) -> str:
    t = (target_name or "").lower()
    if "synthetic dna" in t:
        return "synthetic_DNA"
    if "viral rna" in t or "hpiv" in t or "rsv" in t:
        return "viral_RNA_or_viral_sequence_model"
    if "total bacterial rna" in t or "16s rrna" in t or "smegmatis" in t or "mtc" in t:
        return "bacterial_RNA_or_16S_model"
    if "e. coli" in t or "escherichia" in t:
        return "bacterial_cells_or_bacterial_marker_proxy"
    return "unknown"


def parse_rate_constant(rate_text: str) -> tuple[str, str, str]:
    """Return measurement_type, value, unit for simple kcat/kobs/kc strings."""
    if not rate_text:
        return "metadata_only", "", ""
    m = re.search(
        r"\b(?P<kind>kcat|kobs|kc|rate_constant)\b\s*=\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)\s*(?P<unit>(?:min|h|hr|s)\^-?1)",
        rate_text,
        flags=re.IGNORECASE,
    )
    if not m:
        return "metadata_only", "", ""
    kind = m.group("kind").lower()
    val = m.group("value").replace(",", ".")
    unit = m.group("unit").replace("hr", "h")
    return kind, val, unit


def map_pdf_row(row: pd.Series) -> dict:
    source = text(row, "source") or text(row, "doi")
    return {
        "record_id": text(row, "record_id"),
        "source_id": text(row, "source_id"),
        "source_type": "scientific_paper",
        "source_url": "",
        "source": source,
        "source_location": text(row, "source_location"),
        "sensor_architecture": text(row, "sensor_architecture"),
        "dnazyme_name": text(row, "dnazyme_name"),
        "full_sensor_sequence": text(row, "full_sensor_sequence"),
        "target_name": text(row, "target_name"),
        "target_sequence": text(row, "target_sequence"),
        "target_type": text(row, "target_type") or infer_target_type(text(row, "target_name")),
        "reaction_type": text(row, "reaction_type"),
        "detection_method": text(row, "detection_method"),
        "measurement_type": text(row, "measurement_type"),
        "measurement_value": value(row, "measurement_value"),
        "measurement_unit": text(row, "measurement_unit"),
        "normalized_value_nM": value(row, "lod_nM") if str(row.get("measurement_type", "")).lower() == "lod" else None,
        "lod_nM": value(row, "lod_nM"),
        "signal_to_background_ratio": value(row, "signal_to_background_ratio"),
        "temperature_c": value(row, "temperature_c"),
        "Gibbs_energy": value(row, "Gibbs_energy"),
        "buffer": text(row, "buffer"),
        "pH": value(row, "pH"),
        "Mg_mM": value(row, "Mg_mM"),
        "Na_mM": value(row, "Na_mM"),
        "fluorophore": text(row, "fluorophore"),
        "quencher": text(row, "quencher"),
        "extraction_method": "pdf_manual_curated",
        "extraction_confidence": text(row, "extraction_confidence"),
        "notes": text(row, "extraction_notes"),
    }


def map_web_row(row: pd.Series) -> dict:
    rate_type, rate_value, rate_unit = parse_rate_constant(text(row, "rate_constant"))
    name = text(row, "dnazyme_name")
    notes = "; ".join(
        part for part in [text(row, "selection_reason"), text(row, "notes")] if part
    )
    substrate = text(row, "substrates")
    target_name = "generic RNA substrate"
    if "E. coli" in text(row, "metal_ion_or_cofactor") or "Escherichia" in notes:
        target_name = "Escherichia coli / crude extracellular mixture"
    elif "Clostridium" in notes or "C. difficile" in notes:
        target_name = "Clostridium difficile / crude extracellular mixture"
    source = text(row, "reported_publication_doi") or text(row, "source_url")
    return {
        "record_id": text(row, "record_id"),
        "source_id": text(row, "source_id"),
        "source_type": "database_entry",
        "source_url": text(row, "source_url"),
        "source": source,
        "source_location": text(row, "source_location"),
        "sensor_architecture": "DNAmoreDB_RNA_cleaving_DNAzyme_entry",
        "dnazyme_name": name,
        "full_sensor_sequence": text(row, "catalytic_region"),
        "target_name": target_name,
        "target_sequence": substrate,
        "target_type": infer_target_type(target_name),
        "reaction_type": text(row, "reaction"),
        "detection_method": "database_metadata",
        "measurement_type": rate_type,
        "measurement_value": rate_value,
        "measurement_unit": rate_unit,
        "normalized_value_nM": None,
        "lod_nM": None,
        "signal_to_background_ratio": None,
        "temperature_c": None,
        "Gibbs_energy": None,
        "buffer": text(row, "buffer_conditions"),
        "pH": None,
        "Mg_mM": None,
        "Na_mM": None,
        "fluorophore": "FAM/Fluorescein" if "Fluorescein" in substrate or "FAM" in substrate else "",
        "quencher": "DABCYL/BHQ" if "DABCYL" in substrate or "BHQ" in substrate else "",
        "extraction_method": text(row, "extraction_method") or "web_html_entry_page",
        "extraction_confidence": text(row, "extraction_confidence"),
        "notes": notes,
    }


def build() -> pd.DataFrame:
    rows: list[dict] = []

    if PDF_CSV.is_file():
        pdf_df = pd.read_csv(PDF_CSV)
        rows.extend(map_pdf_row(row) for _, row in pdf_df.iterrows())

    if WEB_CSV.is_file():
        web_df = pd.read_csv(WEB_CSV)
        if len(web_df.columns) > 0:
            rows.extend(map_web_row(row) for _, row in web_df.iterrows())

    columns = load_schema_columns()
    df = pd.DataFrame(rows)
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns]


def main() -> None:
    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(MERGED_PATH, index=False)
    print(f"Wrote {len(df)} rows to {MERGED_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
