# Dataset card - DNA-based nucleic-acid sensor records

## Dataset title

DNA-based sensors for nucleic acid detection dataset

## Dataset summary

This dataset is a tabular collection of experimentally reported records for DNAzyme-based and DNA-based nucleic-acid sensing systems

The dataset includes:

- sensor-performance records extracted from scientific papers;
- LOD values for synthetic DNA/RNA model targets, bacterial RNA / 16S rRNA-related targets, and viral RNA model targets;
- sensitivity-improvement records and other related performance measurements;
- selected DNAmoreDB metadata records for relevant DNAzyme entries;
- sensor and target sequences curated from main articles and supplementary materials.

The main publication-ready file is: `data/processed/dataset.csv`

An additional LOD-only analysis subset is provided as: `data/processed/dataset_lod_only.csv`

## Scientific task

Collect experimentally reported quantitative measurements and structured metadata for DNAzyme-based nucleic-acid sensors

## Record unit

One row = one experimentally reported quantitative measurement for one DNAzyme-based nucleic-acid sensing system or DNAzyme catalytic component under one defined assay condition from one specific source

Most records are quantitative sensor-performance measurements, such as:

- LOD;
- detectable concentration;
- visual detection amount;
- sensitivity improvement factor;
- sensitivity difference factor.

Two web-derived records are `metadata_only` DNAmoreDB records. They are retained as structured database metadata and source-discovery records, not as direct LOD measurements.

## Data sources

Defined in `specs/source_map.json`: journal PDFs, supplementary tables, aptamer databases, metadata aggregators, GitHub releases, and optional ML dataset exports (with license review)

Data sources are defined in `specs/source_map.json`.

The current dataset uses:

- scientific papers;
- supplementary materials;
- DNAmoreDB web/database pages;
- bibliographic aggregators for metadata verification.

Main paper-derived sources include:

- Gerasimova et al. 2013 — deoxyribozyme cascade for visual detection of bacterial RNA;
- Cox et al. 2016 — multifunctional molecular DNA machine for RNA detection;
- Solyanikova et al. 2025 — multicomponent DNA nanomachines for amplification-free viral RNA detection.

Web-derived source:

- DNAmoreDB — selected DNAzyme entries, currently including `10-23` and `RFD-EC1`.

Supplementary files were used to curate sequence information, including sensor components, target sequences, F-sub strands, Hook strands, tile strands, Dza/Dzb components, and MB-DNS / DNM oligonucleotides

## Data extraction procedure

PDF extraction is documented in Practice 3. The script `scripts/extract_pdf.py` produces automatic PDF candidates, while the final verified PDF records are stored in: `data/extracted/pdf_extracted_records.csv`. The manually verified PDF dataset includes values curated from main articles, figures, tables, captions, and supplementary materials.

Web extraction is documented in Practice 4.

The web extraction workflow uses:

- `scripts/extract_web_candidates.py`
- `scripts/select_web_records.py`
- `scripts/extract_web.py`

The web extraction output files are:

- `data/extracted/web_extracted_candidates.csv`
- `data/extracted/web_extracted_records.csv`

## Data cleaning and normalization

The final dataset is built and cleaned with:

- `scripts/build_dataset.py`
- `scripts/clean_dataset.py`
- `scripts/validate_project.py`

The cleaning pipeline is documented in:

`specs/cleaning_pipeline.json`

Cleaning steps include:

- merging PDF and web records;
- mapping heterogeneous source columns into the common schema;
- aligning columns with `specs/dataset_schema.json`;
- normalizing missing values;
- converting compatible concentration units to nM;
- preserving reported units;
- normalizing sequence strings;
- preserving multicomponent sensor annotations;
- removing duplicate records;
- exporting the final dataset.

Reported units are preserved in:

- `measurement_value`
- `measurement_unit`

Comparable concentration values are stored in:

- `normalized_value_nM`
- `lod_nM`

LOD values reported in `ng/uL` are preserved as reported and are not converted to nM, because conversion would require assumptions about total RNA composition and molecular weight.


## Dataset schema

## Dataset schema

Field definitions, data types, and descriptions are stored in: `specs/dataset_schema.json`

The final columns in `data/processed/dataset.csv` follow this schema exactly.

## Validation

Validation rules are defined in: `specs/validation_rules.json`

Validation is run with: `python scripts/validate_project.py`

The validator checks:

- required files exist;
- JSON files are parseable;
- `data/processed/dataset.csv` exists;
- dataset columns match `specs/dataset_schema.json`;
- `record_id` values are non-empty and unique;
- `source_id` values are non-empty;
- `measurement_value` values are numeric or blank;
- `extraction_confidence` values are allowed.

## Known limitations

- The dataset is small and focused on selected DNAzyme/DNM-related nucleic-acid sensing papers
- Not every DNA-based sensor architecture is represented
- DNAmoreDB records are metadata records, not direct LOD records
- LOD values reported in `ng/uL` are not converted to nM
- Some values were manually curated from figures, captions, or supplementary materials
- Some records describe synthetic DNA/RNA model targets rather than clinical samples
- Bacterial RNA / 16S rRNA-related records may involve total RNA or bacterial-marker proxy targets
- Multicomponent sensor sequences are stored as component-labeled strings rather than single continuous sequences
- The dataset is intended for structured comparison and educational data extraction, not for clinical validation

## Recommended use

- comparing LOD values across DNAzyme-based and DNA nanomachine sensor architectures;
- studying how sensor architecture relates to sensitivity;
- practicing scientific data extraction from PDFs, supplementary files, and web databases;
- benchmarking cleaning and validation pipelines for chemical/biological datasets;
- source-discovery for DNAzyme-based nucleic-acid sensing systems.

For direct sensitivity comparison, use: `data/processed/dataset_lod_only.csv` or filter the full dataset by: `measurement_type == "LOD"`

For direct nM-based comparison, additionally require: `lod_nM` is not empty.

## Not recommended use

This dataset is not recommended for:

- clinical decision-making;
- diagnostic performance claims;
- uncritical meta-analysis without rechecking primary sources;
- comparing `metadata_only` records with LOD records;
- converting `ng/uL` total RNA LODs to nM without explicit assumptions;
- commercial reuse of raw third-party source files without checking upstream licenses.

## License

The cleaned dataset is released under CC-BY-4.0. 

See `LICENSE`.

## Citation

See `CITATION.cff`
