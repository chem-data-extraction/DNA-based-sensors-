# Practice 1 — Record definition and dataset schema

## Topic

DNA-based sensors for nucleic acid detection dataset. 

## Scientific task

Collect  experimentally reported quantitative performance measurements of DNA-based sensors for nucleic-acid target detection and SNP/SNV discrimination.

## One-record definition

**One record** = one experimentally reported quantitative performance measurement for one DNA-based sensor design tested against one nucleic-acid target or target variant under one defined assay condition from one source (one row in `data/processed/dataset.csv`).

## Examples of records

| Example | Why it counts |
|---------|----------------|
| LOD `≈ 5.5 nM` for the OC sensor detecting the matched `rs87T` DNA analyte in Cornett et al. 2013 | One numerical detection-limit value for one sensor and one matched target sequence |
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
| sensor architecture | string | yes |
| target name | string | yes |
| target sequence | string | yes |
| reporter probe sequence | string | optional |
| adapter 1_sequence | string | optional |
| adapter 2_sequence | string | optional |
| measurement type | categorical | yes |
| measurement unit | categorical | optional |
| temperature c | float | optional |
| Gibbs energy | floating | yes|
| buffer | string | optional |
| pH | float | optional |
| method | categorical | optional |
| fluorophore | string | optional |
| quencher | string | optional |
| mgcl2_mM | float | optional |
| source | string / DOI / URL | yes |
| notes | string | optional |
