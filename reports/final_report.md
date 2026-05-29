# Final report

## Project summary

**Project title:** DNAzyme-based nucleic-acid sensor records  
**Author:** Nesterova Polina  
**Version:** 0.1.0  
**Repository:** `https://github.com/chem-data-extraction/DNA-based-sensors-`

This project builds a structured, validated dataset of DNAzyme-based and related DNA-based nucleic-acid sensing records. The dataset combines manually curated PDF-derived sensor-performance records with selected web-derived DNAmoreDB metadata records.

The final dataset follows the course pipeline:

**record definition → source map → PDF extraction → web extraction → cleaning and normalization → validation → publication metadata**

## Dataset goal

The dataset supports comparison of DNAzyme-based and DNA-based nucleic-acid sensor designs.

The main scientific question is: **which DNAzyme-based or DNA nanomachine sensing architectures are associated with lower LOD, better sensitivity, and useful target coverage under reported assay conditions?**

The intended audience includes:

- students learning structured scientific data extraction;
- researchers interested in DNAzyme-based sensing systems;
- users comparing LOD values across DNAzyme, BiDZ, DNM, and related architectures;
- developers of extraction/cleaning workflows for chemical and biological datasets.

The primary analysis subset is the LOD-only file: `data/processed/dataset_lod_only.csv`

The full publication-ready dataset is: `data/processed/dataset.csv`

## Source summary

All sources are documented in: `specs/source_map.json`

### Source groups

| Source group | Count / status | Role |
|---|---:|---|
| Scientific papers | 7 mapped, 3 used directly in current processed dataset | Primary source of sensor-performance records |
| Supplementary materials | 3 used directly | Source of sensor and target sequences, assay details, and LOD calculation context |
| Databases | 1 main database | DNAmoreDB used for structured DNAzyme metadata and linked publication records |
| Aggregators | 2 | PubMed and Google Scholar used for discovery and metadata verification |
| GitHub repositories | none confirmed | No directly reusable dataset found |
| ML datasets | none confirmed | No ML-ready dataset directly matching the project scope found |

### Key paper sources used in the processed dataset

| source_id | Source | Role |
|---|---|---|
| `paper_gerasimova_2013_visual_bacterial_rna` | Gerasimova et al. 2013, ChemBioChem | DNAzyme cascade for visual bacterial RNA detection |
| `paper_cox_2016_mdm_rna` | Cox et al. 2016, Chemical Communications | Multifunctional molecular DNA machine for RNA detection |
| `paper_solyanikova_2025_viral_rna_dnm` | Solyanikova et al. 2025, IJMS | Multicomponent DNA nanomachines for viral RNA detection |
| `db_dnamoredb` | DNAmoreDB | Structured DNAzyme metadata and selected DNAzyme entry pages |

### Supplementary materials

Supplementary materials were used for:

- Dza/Dzb sequences;
- F-sub and F-sub-1 sequences;
- Hook sequences;
- tile strands;
- MB-DNS components;
- HPIV/RSV analytes;
- bacterial RNA / 16S rRNA-related target sequences;
- assay and LOD calculation context.

## Extraction summary

### PDF extraction

PDF extraction is documented in: `reports/practice_03_pdf_extraction.md`

Main files:

- `specs/pdf_extraction_manifest.json`
- `scripts/extract_pdf.py`
- `data/extracted/pdf_extracted_candidates.csv`
- `data/extracted/pdf_extracted_records.csv`

The script `scripts/extract_pdf.py` performs automatic first-pass candidate extraction from selected PDFs. It searches for LOD-like and sensitivity-related statements in article text.

The final file used in the cleaning pipeline is: `data/extracted/pdf_extracted_records.csv`

This file was curated manually from selected papers and supplementary materials. It must be present before running the build and cleaning pipeline.

### Web extraction

Web extraction is documented in: `reports/practice_04_web_extraction.md`

Main files:

- `specs/web_extraction_manifest.json`
- `scripts/extract_web_candidates.py`
- `scripts/select_web_records.py`
- `scripts/extract_web.py`
- `data/extracted/web_extracted_candidates.csv`
- `data/extracted/web_extracted_records.csv`

The web extraction workflow uses DNAmoreDB.

The first script extracts algorithmically filtered candidates from DNAmoreDB using general rules based on RNA cleavage, bacterial/RNA context, and sensor/detection/readout keywords.

The second script selects expert-approved entries from the candidate table and extracts detailed fields from individual DNAmoreDB entry pages.

The compatibility wrapper `scripts/extract_web.py` runs both web steps.

The current web records file contains 2 selected DNAmoreDB entries:

- `10-23`
- `RFD-EC1`

These records are retained as `metadata_only` database records. They are useful for source discovery and DNAzyme metadata, but they are not used for direct LOD comparison.

## Cleaning and normalization summary

Cleaning is documented in: `reports/practice_05_cleaning_publication.md`

The cleaning pipeline is defined in: `specs/cleaning_pipeline.json`

Main scripts:

- `scripts/build_dataset.py`
- `scripts/clean_dataset.py`
- `scripts/validate_project.py`

### Pipeline steps

The cleaning pipeline applies the following steps:

1. Merge PDF and web extracted records
2. Map heterogeneous source columns into the common schema
3. Align columns to `specs/dataset_schema.json`
4. Normalize missing values
5. Coerce numeric columns when possible
6. Convert compatible concentration units to nM
7. Preserve non-convertible units as reported
8. Normalize sequence-containing fields
9. Preserve multicomponent sequence labels
10. Deduplicate records
11. Export the full processed dataset
12. Export an LOD-only analysis subset
13. Validate the final dataset

### Unit normalization

Reported values are preserved in:  `measurement_value` and `measurement_unit`

Converted values are stored in: `normalized_value_nM` and `lod_nM`

### Sequence normalization

Sequence-containing fields are uppercased and whitespace is cleaned. Component labels are preserved. This is important because multicomponent DNAzyme and DNM sensors contain multiple strands, such as:

- Dza;
- Dzb;
- F-sub;
- F-sub-1;
- Hook;
- tile strands;
- analyte-binding arms;
- molecular beacon components.

Therefore, `full_sensor_sequence` is stored as component-labeled strings rather than a single artificial concatenated sequence.

### Deduplication outcome

Deduplication uses `record_id` as the primary key.

A secondary duplicate check considers:

- `source_id`
- `sensor_architecture`
- `dnazyme_name`
- `target_name`
- `measurement_type`
- `measurement_value`
- `measurement_unit`
- `source_location`

Different assay conditions are preserved as separate records. For example, the same sensor tested at different incubation times remains as multiple records. The final cleaned dataset contains 40 records.

## Validation summary

Validation rules are documented in: `specs/validation_rules.json`

Validation was run with: `python scripts/validate_project.py`

The validator checks:

- required files exist;
- JSON files are parseable;
- `data/processed/dataset.csv` exists;
- dataset columns match `specs/dataset_schema.json`;
- `record_id` values are non-empty and unique;
- `source_id` values are non-empty;
- `measurement_value` values are numeric or blank;
- `extraction_confidence` values are allowed.

## Limitations

The dataset has several limitation: 

First, the dataset is small and focused on selected DNAzyme / DNA nanomachine papers rather than all possible DNA-based sensors

Second, DNAmoreDB is not a direct LOD database. The two DNAmoreDB records are `metadata_only` records and should not be compared directly with LOD records

Third, some LOD values are reported in `ng/uL`. These values are preserved as reported but are not converted to nM

Fourth, some values were manually curated from figures, captions, tables, and supplementary files. These records have extraction confidence fields and notes describing provenance

Fifth, some records use synthetic DNA/RNA model targets rather than clinical samples

## Final artifacts

| Artifact | Path |
|---|---|
| Processed dataset | `data/processed/dataset.csv` |
| LOD-only subset | `data/processed/dataset_lod_only.csv` |
| Schema | `specs/dataset_schema.json` |
| Source map | `specs/source_map.json` |
| PDF extraction manifest | `specs/pdf_extraction_manifest.json` |
| Web extraction manifest | `specs/web_extraction_manifest.json` |
| Cleaning pipeline | `specs/cleaning_pipeline.json` |
| Validation rules | `specs/validation_rules.json` |
| PDF extracted records | `data/extracted/pdf_extracted_records.csv` |
| Web extracted records | `data/extracted/web_extracted_records.csv` |
| Dataset card | `dataset_card.md` |
| Citation | `CITATION.cff` |
| License | `LICENSE` |
| Practice 1 report | `reports/practice_01_record_and_schema.md` |
| Practice 2 report | `reports/practice_02_source_map.md` |
| Practice 3 report | `reports/practice_03_pdf_extraction.md` |
| Practice 4 report | `reports/practice_04_web_extraction.md` |
| Practice 5 report | `reports/practice_05_cleaning_publication.md` |
