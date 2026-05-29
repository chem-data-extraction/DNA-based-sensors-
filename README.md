# DNA-based sensors for nucleic acid detection dataset

Publication-ready dataset project for the course **Extraction and preparation of chemical information**.

This repository contains a structured dataset of DNAzyme-based and DNA-based nucleic-acid sensing records. The project follows the course pipeline: record definition, source mapping, PDF extraction, web extraction, cleaning/normalization, validation, and publication metadata.

## Scientific task

Collect experimentally reported quantitative measurements and structured metadata for DNAzyme-based nucleic-acid sensors.

## What is one record?

**One record** = one extracted measurement or structured metadata record for one DNAzyme-based or DNA-based nucleic-acid sensing system, DNAzyme component, or related assay condition from one source.

Most rows describe sensor-performance values, such as LOD, detectable concentration, visual detection amount, or sensitivity improvement factor.

Two rows are selected DNAmoreDB `metadata_only` records. These web-derived records are kept as structured DNAzyme metadata/source-discovery records and are not used for direct LOD comparison.

See:

- `project.json`
- `reports/practice_01_record_and_schema.md`
- `specs/dataset_schema.json`

## Repository structure

| Path | Role |
|---|---|
| `project.json` | Machine-readable project metadata |
| `specs/` | Dataset schema, source map, extraction manifests, cleaning pipeline, validation rules |
| `data/raw/` | Unmodified PDFs, supplementary files, web snapshots, external exports |
| `data/extracted/` | Extracted PDF/web records, candidate tables, and `extraction_log.jsonl` |
| `data/interim/` | Merged table before final cleaning |
| `data/processed/` | Publication-ready datasets |
| `scripts/` | Extraction, build, cleaning, and validation scripts |
| `reports/` | Human-readable practice reports and final report |
| `notebooks/` | Optional exploration only |
| `tests/` | Pytest checks for required artifacts |

Formats:

- JSON for specs and manifests;
- CSV for tabular data;
- Python for pipelines;
- Markdown for reports and documentation.

## Five course practices

Develop the repository in five steps (see `reports/`):

1. **Record definition and dataset schema** — `specs/dataset_schema.json`, Practice 1 report  
2. **Source map** — `specs/source_map.json`, Practice 2 report  
3. **PDF extraction** — `specs/pdf_extraction_manifest.json`, `scripts/extract_pdf.py`, Practice 3 report  
4. **Web extraction** — `specs/web_extraction_manifest.json`, `scripts/extract_web.py`, Practice 4 report  
5. **Cleaning, normalization and publication** — `specs/cleaning_pipeline.json`, cleaning scripts, Practice 5 report  

## Data pipeline

The full data pipeline is:

```text

`raw PDF / supplementary / web sources`

→ extraction scripts and manual curation

→ `data/extracted/*.csv`

→ `scripts/build_dataset.py`

→ `data/interim/merged_records.csv`

→ `scripts/clean_dataset.py`

→ `data/processed/dataset.csv`

→ `data/processed/dataset_lod_only.csv`

→ `scripts/validate_project.py`

```

## How to install dependencies

From the repository root: `pip install -r requirements.txt`

## How to run extraction

Run PDF candidate extraction: `python scripts/extract_pdf.py`

This writes automatic candidates to: `data/extracted/pdf_extracted_candidates.csv`

The curated file used for final processing is: `data/extracted/pdf_extracted_records.csv`

This curated PDF file is manually prepared and must be present before running the cleaning pipeline.

Run web extraction: `python scripts/extract_web.py` or run the two web steps separately: `python scripts/extract_web_candidates.py` and `python scripts/select_web_records.py`

This produces:

- `data/extracted/web_extracted_candidates.csv`
- `data/extracted/web_extracted_records.csv`

## How to build and clean the dataset

From the repository root: `python scripts/build_dataset.py` and `python scripts/clean_dataset.py`

This produces:

- `data/interim/merged_records.csv`
- `data/processed/dataset.csv`
- `data/processed/dataset_lod_only.csv`

## How to validate

Run: `python scripts/validate_project.py`

Expected result: `Validation passed`

## Required final artifacts

## Required final artifacts

Before submission, the repository should include:

- `data/processed/dataset.csv`
- `data/processed/dataset_lod_only.csv`
- `specs/dataset_schema.json`
- `specs/source_map.json`
- `specs/pdf_extraction_manifest.json`
- `specs/web_extraction_manifest.json`
- `specs/cleaning_pipeline.json`
- `specs/validation_rules.json`
- `data/extracted/pdf_extracted_records.csv`
- `data/extracted/web_extracted_records.csv`
- `reports/practice_01_record_and_schema.md`
- `reports/practice_02_source_map.md`
- `reports/practice_03_pdf_extraction.md`
- `reports/practice_04_web_extraction.md`
- `reports/practice_05_cleaning_publication.md`
- `reports/final_report.md`
- `dataset_card.md`
- `LICENSE`
- `CITATION.cff`

## License and citation

The cleaned dataset is released under CC-BY-4.0.

See: `LICENSE` and `CITATION.cff`
