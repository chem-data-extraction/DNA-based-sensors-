# Processed data

This folder holds the **publication-ready** dataset: one row per record, columns aligned with `specs/dataset_schema.json`.

## Main file

- `dataset.csv` — final dataset produced by `scripts/build_dataset.py` and `scripts/clean_dataset.py`, validated with `scripts/validate_project.py`

This file combines:

manually verified PDF records from data/extracted/pdf_extracted_records.csv;
selected web records from data/extracted/web_extracted_records.csv

The current dataset contains both sensor-performance records and selected DNAmoreDB metadata records

### Additional analysis file

`dataset_lod_only.csv` — LOD-only subset produced by `scripts/clean_dataset.py`

This file contains only records where: measurement_type = LOD

LOD values reported in mass units such as ng/uL are preserved as reported and are not converted to nM, because conversion would require assumptions about RNA composition and molecular weight
