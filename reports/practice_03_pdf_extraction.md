# Practice 3 — PDF extraction

> Align with `specs/pdf_extraction_manifest.json` and `data/extracted/pdf_extracted_records.csv`.

## Selected PDF sources

| source_id | pdf_id | Year (approx.) | Path |
|---|---|---:|---|
| paper_gerasimova_2013_vis_al_bacterial_rna | gerasimova_2013_deoxyribozyme_cascade_bacterial_rna | 2013 | data/raw/pdf/nihms534513.pdf |
| paper_cox_2016_mdm_rna | cox_2016_multifunctional_molecular_dna_machine_rna | 2016 | data/raw/pdf/nihms912297.pdf |
| paper_solyanikova_2025_viral_rna_dnm | solyanikova_2025_multicomponent_dna_nanomachines_viral_rna | 2025 | data/raw/pdf/ijms-26-03652.pdf |


## Why these PDFs were selected

These three PDFs were selected because they represent three different time periods in the development of DNAzyme-based nucleic-acid sensors and because each of them contains experimentally reported quantitative data that can be extracted into the dataset

**Gerasimova et al. 2013** was selected as the older source. It reports a deoxyribozyme cascade for visual detection of bacterial RNA. This paper is relevant because it contains early DNAzyme-cascade sensor data for bacterial 16S rRNA detection, including LOD values for synthetic DNA analytes and total bacterial RNA. It also contains useful experimental conditions and sequence information

**Cox et al. 2016** was selected as the middle-period source. It reports a multifunctional molecular DNA machine for RNA detection. This paper is especially useful because it contains a clear LOD table comparing the traditional binary deoxyribozyme probe and several molecular DNA machine variants. The table provides multiple extractable records for different analytes and incubation times

**Solyanikova et al. 2025** was selected as the recent source. It reports multicomponent DNA nanomachines for amplification-free viral RNA detection. This paper is open access and contains many directly extractable LOD values for HPIV and RSV detection by 6DNM and 4DNM sensors, as well as methodological details, buffer conditions, incubation times, and supplementary raw data references

## Pages used

| pdf_id | Pages used | Content used |
|---|---|---|
| gerasimova_2013_deoxyribozyme_cascade_bacterial_rna | 1–4, 9 | Abstract and results text with LOD values; Figure 1 sensor/cascade design; Figure 2 and related text for RNA detection; Table 1 with oligonucleotide sequences; methods and assay conditions |
| cox_2016_multifunctional_molecular_dna_machine_rna | 1–4, 9 | Abstract and results text with 24-fold improvement statement; Figure 2 fluorescence kinetics; Table 1 with LOD values for BiDZ and MDMR1 variants at 20 min and 60 min; experimental conditions and supplementary-information references |
| solyanikova_2025_multicomponent_dna_nanomachines_viral_rna | 4, 7, 8, 10–14 | MB-DNS LOD text; 6DNM LOD values for HPIV and RSV; 4DNM comparison LOD values; Figure 8 and Figure S4 references; Figure 9 viral RNA detection; Table 1 comparison of assay parameters; methods, buffer composition, and LOD calculation procedure |

## Extraction methods

### Tools considered

- **PyMuPDF** — for extracting text from selected PDF pages
- **pdfplumber** — for extracting text and potentially simple tables
- **Camelot** — for structured table extraction when tables have clear borders
- **Tabula** — for table extraction from PDF, if needed
- **Manual verification** — for figure values, table cleanup, source-location checking, ambiguous units, and candidate validation

## Extracted fields

## Extracted fields

The extracted PDF content was mapped to the dataset schema as follows:

| PDF content | Dataset field |
|---|---|
| Paper/source identifier | `source_id` |
| PDF identifier | `pdf_id` |
| Page, figure, table, or section | `page`, `source_location` |
| Sensor architecture | `sensor_architecture` |
| DNAzyme or machine name | `dnazyme_name` |
| Target/analyte name | `target_name` |
| Target sequence, when available | `target_sequence` |
| Reaction chemistry | `reaction_type` |
| Detection format | `detection_method` |
| Reported LOD, fold improvement, or detection value | `measurement_type` |
| Numeric measurement | `measurement_value` |
| Original unit | `measurement_unit` |
| LOD converted to nM where possible | `lod_nM` |
| Buffer and pH | `buffer`, `pH` |
| Metal-ion conditions | `Mg_mM`, `Na_mM` |
| Fluorophore and quencher | `fluorophore`, `quencher` |
| Extraction method | `extraction_method` |
| Confidence after verification | `extraction_confidence` |
| Comments and manual corrections | `extraction_notes` |

Manual corrections included:

- Assigning specific targets to values reported in combined sentences, for example HPIV versus RSV LOD values in Solyanikova et al. 2025
- Splitting paired LOD statements into separate records, for example:
  - HPIV 6DNM, 1 h;
  - HPIV 6DNM, 3 h;
  - RSV 6DNM, 1 h;
  - RSV 6DNM, 3 h.
- Converting LOD values from pM to nM in the helper field `lod_nM`
- Leaving mass-unit LOD values such as `ng/μL` unconverted because conversion to nM would require target length, molecular weight, and assumptions about RNA composition
- Marking approximate values in `extraction_notes`
- Marking values from figures or non-tabulated text as lower confidence than values from explicit tables
- Rejecting false positives where the script detected an unrelated number near the word `LOD`

## Extraction problems

- the script sometimes captured values that were not measurements. For example, incubation times such as `15 min` or `60 min` can appear near LOD text and be incorrectly detected as measurement values. These records were rejected during candidate review
- some papers report paired values in a single sentence. For example, one sentence may contain both HPIV and RSV LODs and both 1 h and 3 h incubation values. The script can detect some of these values, but manual splitting is required to assign each value to the correct target and condition
- Cox et al. 2016 Table 1 contains multiple LOD values across sensor variants, analytes, and incubation times. Generic regex extraction cannot reliably reconstruct this table. Therefore, the table was manually transcribed into structured records
- some values are shown in figures, figure captions, or supplementary figures rather than clean main-text tables. These require manual extraction or future figure digitization
- some fold-change values describe sensitivity improvement relative to another sensor, while others describe background performance or context. These were included only when they directly described sensor performance
- full DNAzyme, substrate, and target sequences are often not fully available in the main-text PDF. Supplementary materials are needed for complete sequence extraction
- the PDFs include fluorescence, visual/colorimetric, and catalytic signal-amplification readouts. These are not directly comparable unless `detection_method`, `measurement_type`, and assay conditions are preserved

## Output files

| File | Description |
|---|---|
| `specs/pdf_extraction_manifest.json` | Machine-readable manifest listing selected PDF sources, paths, pages used, extraction methods, and expected fields |
| `scripts/extract_pdf.py` | PDF extraction script using PyMuPDF and regex-based candidate detection |
| `data/extracted/pdf_extracted_candidates.csv` | Automatically extracted candidate records from PDF text |
| `data/extracted/pdf_extracted_records.csv` | Final manually verified PDF-extracted records used in later pipeline steps |
| `data/extracted/extraction_log.jsonl` | Extraction log containing script runs, errors, manual-verification notes, and output paths |
| `data/raw/pdf/nihms534513.pdf` | Raw PDF for Gerasimova et al. 2013 |
| `data/raw/pdf/nihms912297.pdf` | Raw PDF for Cox et al. 2016 |
| `data/raw/pdf/ijms-26-03652.pdf` | Raw PDF for Solyanikova et al. 2025 |
