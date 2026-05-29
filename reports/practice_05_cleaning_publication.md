# Practice 5 — Cleaning, normalization and publication

> Follow `specs/cleaning_pipeline.json`. Run `scripts/clean_dataset.py` and `scripts/validate_project.py`.

## Input files

- `data/extracted/pdf_extracted_records.csv`
- `data/extracted/web_extracted_records.csv`
- `data/extracted/downoaded_records.csv`
- `data/interim/merged_records.csv`

## Cleaning steps

## Cleaning steps

The cleaning workflow follows the steps documented in `specs/cleaning_pipeline.json`

### 1. Merge sources

PDF and web records are combined into one intermediate table

The script reads `data/extracted/pdf_extracted_records.csv` and `data/extracted/web_extracted_records.csv`, then writes `data/interim/merged_records.csv`

PDF records and web records originally have different column structures, so `scripts/build_dataset.py` maps both formats into the shared dataset schema

PDF records are treated as `source_type = scientific_paper` and `extraction_method = pdf_manual_curated`

Web records are treated as `source_type = database_entry` and `extraction_method = web_html_entry_page`

The web records are kept as `metadata_only` records because DNAmoreDB provides structured DNAzyme metadata rather than direct LOD measurements

### 2. Align columns to schema

The cleaning script reads the final expected column list from `specs/dataset_schema.json`

All required schema columns are added if missing, and the final column order is forced to match the schema exactly

This ensures that `data/processed/dataset.csv` can be validated against `specs/dataset_schema.json`

### 3. Normalize missing values

Different missing-value tokens are standardized

The following values are treated as missing: `""`, `"na"`, `"n/a"`, `"none"`, `"null"`, `"-"`, and `"nan"`

This avoids mixing several different representations of missing data in the final CSV

### 4. Normalize numeric values

Numeric fields are cleaned where possible

The following columns are treated as numeric when present: `measurement_value`, `normalized_value_nM`, `lod_nM`, `signal_to_background_ratio`, `temperature_c`, `Gibbs_energy`, `pH`, `Mg_mM`, and `Na_mM`

Values such as `0,4` are normalized to `0.4` where applicable. Non-numeric values are not forced into numeric form

### 5. Normalize units

Reported units are preserved in `measurement_value` and `measurement_unit`

For concentration values, the cleaning script additionally creates normalized nM values in `normalized_value_nM` and `lod_nM`

The conversion rules are:

| Reported unit | Conversion to nM |
|---|---:|
| `pM` | value × 0.001 |
| `nM` | value × 1 |
| `uM`, `µM`, `μM` | value × 1000 |
| `M` | value × 1,000,000,000 |

Values reported in non-molar units are preserved but not converted

Examples of non-converted units are `ng/uL`, `ng`, `fold`, `CFU`, `cells`, and `min^-1`

LOD values reported as `ng/uL` are kept because they refer to total RNA samples. Converting total RNA mass concentration to nM would require assumptions about RNA composition, molecular weight, and the fraction of target 16S rRNA. Therefore, these records remain in the dataset, but `lod_nM` is left empty for them

### 6. Normalize sequences

Sequence fields are cleaned while preserving multicomponent sensor structure

The main sequence fields are `full_sensor_sequence` and `target_sequence`

For simple target sequences, whitespace is removed and sequences are uppercased

For multicomponent sensors, component labels are preserved, because the sensor is not a single continuous strand. For example, a multicomponent record may contain `DZA_MTC=...; DZB_MTC=...; IPDZ=...; PDZ=...`

This format is retained because DNAzyme and DNM sensors are often composed of several strands: Dza, Dzb, F-sub, Hook, tile strands, analyte-binding arms, and other components

Sequence information was curated from supplementary materials for the selected PDF sources

### 7. Deduplicate records

Deduplication is performed in two ways

First, duplicate `record_id` values are removed

Second, a semantic duplicate check can use fields such as `source_id`, `sensor_architecture`, `dnazyme_name`, `target_name`, `measurement_type`, `measurement_value`, `measurement_unit`, and `source_location`

Different assay conditions are not removed as duplicates. For example, the same sensor tested after 1 h and 3 h incubation remains as two separate records

### 8. Export final dataset

The cleaned dataset is written to `data/processed/dataset.csv`

The LOD-only subset is written to `data/processed/dataset_lod_only.csv`

The LOD-only file contains only records where `measurement_type = LOD`. It is intended for sensitivity comparison

## Validation results

## Validation results

Validation was run with `python scripts/validate_project.py`

The validation result was: `Validation passed`

The validator checks that required project files exist, JSON files are parseable, `data/processed/dataset.csv` exists, dataset columns match `specs/dataset_schema.json`, `record_id` values are non-empty and unique, `source_id` values are non-empty, `measurement_value` values are numeric or empty, and `extraction_confidence` values are within the allowed set

## Final dataset description

Final processed dataset: `data/processed/dataset.csv`

LOD-only analysis subset: `data/processed/dataset_lod_only.csv`

Current row count:

| File | Rows | Description |
|---|---:|---|
| `data/processed/dataset.csv` | 40 | Full cleaned dataset |
| `data/processed/dataset_lod_only.csv` | 30 | LOD-only subset |

Source breakdown in `dataset.csv`:

| source_type | Rows |
|---|---:|
| `scientific_paper` | 38 |
| `database_entry` | 2 |


The dataset includes records for DNAzyme-based and DNA nanomachine-based sensing systems targeting synthetic DNA analytes, bacterial RNA / 16S rRNA-related targets, and viral RNA model targets

The two `metadata_only` records come from DNAmoreDB and are retained as structured database metadata records for relevant DNAzyme entries. They are not used for direct LOD comparison

For sensitivity analysis, the recommended subset is `measurement_type == "LOD"`

For direct nM-based sensitivity comparison, the recommended subset is `measurement_type == "LOD"` and `lod_nM` is not empty
