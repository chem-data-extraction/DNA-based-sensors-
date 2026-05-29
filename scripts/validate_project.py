#!/usr/bin/env python3
"""Validate project artifacts and final dataset"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "project.json",
    "specs/dataset_schema.json",
    "specs/source_map.json",
    "specs/pdf_extraction_manifest.json",
    "specs/web_extraction_manifest.json",
    "specs/cleaning_pipeline.json",
    "specs/validation_rules.json",
    "data/extracted/pdf_extracted_records.csv",
    "data/extracted/web_extracted_records.csv",
    "data/processed/dataset.csv",
    "scripts/build_dataset.py",
    "scripts/clean_dataset.py",
]
CONFIDENCE_ALLOWED = {"", "high", "medium", "low", "unknown"}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def schema_field_names(schema: dict) -> list[str]:
    return [field["name"] for field in schema["fields"]]


def source_ids_from_map(source_map: dict) -> set[str]:
    ids: set[str] = set()
    groups = source_map.get("source_groups", {})
    if isinstance(groups, dict):
        for group_sources in groups.values():
            if isinstance(group_sources, list):
                for entry in group_sources:
                    sid = entry.get("source_id") if isinstance(entry, dict) else None
                    if sid:
                        ids.add(str(sid))
    return ids


def check_required_files(root: Path = ROOT) -> list[str]:
    return [f"Missing required file: {rel}" for rel in REQUIRED_FILES if not (root / rel).is_file()]


def check_json_parseable(root: Path = ROOT) -> list[str]:
    issues = []
    for path in root.rglob("*.json"):
        if any(skip in path.parts for skip in (".pytest_cache", ".venv", "venv")):
            continue
        try:
            load_json(path)
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON: {path.relative_to(root)} ({exc})")
    return issues


def check_numeric_or_blank(df: pd.DataFrame, col: str) -> list[str]:
    issues = []
    if col not in df.columns:
        return issues
    for idx, val in df[col].items():
        if pd.isna(val) or str(val).strip() == "":
            continue
        try:
            float(val)
        except (TypeError, ValueError):
            issues.append(f"{col} not numeric at row {idx}: {val!r}")
    return issues


def validate(root: Path = ROOT) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(check_required_files(root))
    errors.extend(check_json_parseable(root))

    dataset_path = root / "data/processed/dataset.csv"
    schema_path = root / "specs/dataset_schema.json"
    source_map_path = root / "specs/source_map.json"
    if not dataset_path.is_file() or not schema_path.is_file():
        return errors, warnings

    schema = load_json(schema_path)
    expected = schema_field_names(schema)
    df = pd.read_csv(dataset_path, keep_default_na=False)

    if list(df.columns) != expected:
        errors.append(f"Dataset columns do not match schema. Expected {expected}, got {list(df.columns)}")

    if "record_id" in df.columns:
        if (df["record_id"].astype(str).str.strip() == "").any():
            errors.append("record_id contains empty values")
        if df["record_id"].duplicated().any():
            errors.append(f"Duplicate record_id values: {df.loc[df['record_id'].duplicated(), 'record_id'].tolist()}")

    if "source_id" in df.columns:
        if (df["source_id"].astype(str).str.strip() == "").any():
            errors.append("source_id contains empty values")
        if source_map_path.is_file():
            valid_ids = source_ids_from_map(load_json(source_map_path))
            if valid_ids:
                unknown = set(df["source_id"].astype(str)) - valid_ids
                if unknown:
                    warnings.append(f"source_id not in source map: {sorted(unknown)}")

    for col in ["measurement_value", "normalized_value_nM", "lod_nM"]:
        errors.extend(check_numeric_or_blank(df, col))

    if "extraction_confidence" in df.columns:
        unexpected = sorted(set(v for v in df["extraction_confidence"].astype(str).str.lower() if v not in CONFIDENCE_ALLOWED))
        if unexpected:
            warnings.append(f"Unexpected extraction_confidence values: {unexpected}")

    return errors, warnings


def main() -> int:
    errors, warnings = validate()
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"\nValidation failed with {len(errors)} error(s).")
        return 1
    print("Validation passed.")
    if warnings:
        print(f"({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())

    sys.exit(main())
