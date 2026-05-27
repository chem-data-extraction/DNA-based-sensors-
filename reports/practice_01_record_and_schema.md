# Practice 1 — Record definition and dataset schema

## Topic

DNA-based sensors for nucleic acid detection dataset. 

## Scientific task

Collect experimentally reported quantitative measurements and structured metadata for DNAzyme-based nucleic-acid sensors.

## One-record definition

**One record** = one experimentally reported quantitative measurement for one DNAzyme-based nucleic-acid sensing system or DNAzyme catalytic component under one defined assay condition from one specific source (one row in `data/processed/dataset.csv`).

## Examples of records

| Example | Why it counts |
|---------|----------------|
| LOD `≈ 0.3 pM` for detection of E. coli 16S RNA using a multi-DNAzyme “deoxyribozymes-on-a-string” design. | One quantitative LOD measurement for one DNAzyme-based RNA detection system. |
| Molecular-beacon-based X sensor detecting *E. coli* 16S rRNA with LOD `~0.17 nM` | One experimentally reported detection-limit measurement for an RNA target |

## Non-record examples

| Example | Why it is not a record |
|---------|-------------------------|
| A list of probe sequences without signal, LOD, selectivity, Fm/Fmm, ΔT, or assay-performance value | Sequence alone is not a performance measurement |
| A predicted ΔG, Tm, ΔH, or ΔS value calculated by software without experimental sensor validation | Computational feature only. It can be stored as an optional descriptor, but it is not a dataset record by itself |
| A docking/simulation result showing possible hybridization but no experimental fluorescence | No experimental sensing measurement |

## Dataset fields

The schema fields are represented in `specs/dataset_schema.json`. The file is updated manually when the fields are changed.

## Minimal viable schema

| Field | Type | Required? |
|---|---|---|
| record id | string | yes |
| source id | string | yes |
| sensor architecture | categorical | yes |
| dnazyme name | string | optional |
| full sensor sequence | string | optional |
| target name | string | yes |
| target sequence | string | optional |
| reaction type | categorical | optional |
| detection method | categorical | yes |
| measurement type | categorical | yes |
| measurement value | float | yes |
| measurement unit |string | yes |
| lod nM | float | optional |
| signal to background ratio | float | optional |
| temperature c | float | optional |
| Gibbs energy | float | optional |
| buffer | string | optional |
| pH | float | optional |
| Mg mM | float | optional |
| Na mM | float | optional |
| fluorophore | string | optional |
| quencher | string | optional |
| source | string / DOI / URL | yes |
| source location | string | optional |
| notes | string | optional |
