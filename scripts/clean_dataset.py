#!/usr/bin/env python3
"""Clean, normalize, deduplicate, and export the final dataset"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MERGED_PATH = ROOT / "data/interim/merged_records.csv"
SCHEMA_PATH = ROOT / "specs/dataset_schema.json"
DATASET_PATH = ROOT / "data/processed/dataset.csv"

MISSING_TOKENS = {"", "na", "n/a", "none", "null", "-", "nan", "NaN"}
NUMERIC_COLUMNS = [
    "measurement_value",
    "normalized_value_nM",
    "lod_nM",
    "signal_to_background_ratio",
    "temperature_c",
    "Gibbs_energy",
    "pH",
    "Mg_mM",
    "Na_mM",
]
UNIT_TO_NM = {
    "nm": 1.0,
    "nanomolar": 1.0,
    "pm": 0.001,
    "picomolar": 0.001,
    "um": 1000.0,
    "µm": 1000.0,
    "μm": 1000.0,
    "micromolar": 1000.0,
    "m": 1_000_000_000.0,
    "molar": 1_000_000_000.0,
}


def load_schema_columns() -> list[str]:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    return [field["name"] for field in schema["fields"]]


def normalize_missing(value: Any) -> Any:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in MISSING_TOKENS:
        return ""
    return text


def normalize_sequence_text(value: Any) -> str:
    """Uppercase sequence-like fields while preserving component labels and modifications"""
    value = normalize_missing(value)
    if value == "":
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", "", text)
    text = text.replace("‘", "'").replace("’", "'")
    return text.upper()


def to_float(value: Any):
    value = normalize_missing(value)
    if value == "":
        return ""
    text = str(value).replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return ""


def normalize_to_nm(value: Any, unit: Any):
    value = to_float(value)
    if value == "":
        return ""
    unit = normalize_missing(unit).lower().replace(" ", "")
    factor = UNIT_TO_NM.get(unit)
    if factor is None:
        return ""
    return value * factor


def build_if_needed() -> pd.DataFrame:
    build_path = ROOT / "scripts" / "build_dataset.py"
    spec = importlib.util.spec_from_file_location("build_dataset", build_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {build_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    df = module.build()
    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(MERGED_PATH, index=False)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    columns = load_schema_columns()
    out = df.copy()

    for col in columns:
        if col not in out.columns:
            out[col] = ""
    out = out[columns]

    for col in out.columns:
        out[col] = out[col].map(normalize_missing)

    for col in ["full_sensor_sequence", "target_sequence"]:
        if col in out.columns:
            out[col] = out[col].map(normalize_sequence_text)

    if "measurement_value" in out.columns and "measurement_unit" in out.columns:
        calculated = [normalize_to_nm(v, u) for v, u in zip(out["measurement_value"], out["measurement_unit"])]
        out["normalized_value_nM"] = [existing if normalize_missing(existing) != "" else calc for existing, calc in zip(out["normalized_value_nM"], calculated)]

    if "lod_nM" in out.columns:
        new_lod = []
        for _, row in out.iterrows():
            existing = normalize_missing(row.get("lod_nM", ""))
            if existing != "":
                new_lod.append(existing)
            elif str(row.get("measurement_type", "")).lower() == "lod":
                new_lod.append(normalize_to_nm(row.get("measurement_value", ""), row.get("measurement_unit", "")))
            else:
                new_lod.append("")
        out["lod_nM"] = new_lod

    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = out[col].map(to_float)

    if "extraction_confidence" in out.columns:
        out["extraction_confidence"] = out["extraction_confidence"].str.lower().replace({"":"unknown"})

    out = out[out["record_id"].astype(str).str.strip() != ""].copy()

    out = out.drop_duplicates(subset=["record_id"], keep="first")

    secondary_keys = [
        "source_id", "sensor_architecture", "dnazyme_name", "target_name",
        "measurement_type", "measurement_value", "measurement_unit", "source_location"
    ]
    existing_keys = [k for k in secondary_keys if k in out.columns]
    out = out.drop_duplicates(subset=existing_keys, keep="first")

    return out[columns]

def main() -> None:
    df = build_if_needed()
    cleaned = clean_dataframe(df)
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(DATASET_PATH, index=False)
    print(f"Wrote {len(cleaned)} cleaned rows to {DATASET_PATH.relative_to(ROOT)}")

    LOD_ONLY_PATH = ROOT / "data/processed/dataset_lod_only.csv"
    lod_only = cleaned[cleaned["measurement_type"].astype(str).str.upper() == "LOD"]
    lod_only.to_csv(LOD_ONLY_PATH, index=False)
    print(f"Wrote {len(lod_only)} LOD-only rows to {LOD_ONLY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
