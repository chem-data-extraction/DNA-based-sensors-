# Practice 4 — Web extraction

> Align with `specs/web_extraction_manifest.json` and `data/extracted/web_extracted_records.csv`.

## Selected web sites

| source_id | page_id | URL |
|---|---|---|
| db_dnamoredb | dnamoredb_home | https://www.genesilico.pl/DNAmoreDB/ |
| db_dnamoredb | dnamoredb_api_dnazymes | https://www.genesilico.pl/DNAmoreDB/api/dnazymes |
| db_dnamoredb | dnamoredb_rna_search | https://www.genesilico.pl/DNAmoreDB/dnazymes?q=RNA |
| db_dnamoredb | dnamoredb_entry_10_23 | https://www.genesilico.pl/DNAmoreDB/dnazyme/445/ |
| db_dnamoredb | dnamoredb_entry_rfd_ec1 | https://www.genesilico.pl/DNAmoreDB/dnazyme/1974/ |

## Why these sites were selected

DNAmoreDB was selected as the main web source because it is a structured database of DNAzymes. It contains DNAzyme names, reaction types, catalytic regions, substrates, products, metal ions or cofactors, buffer conditions, notes, and links to primary publications.

This web source complements the PDF extraction step. The PDF extraction step focused on manually verified sensor-performance measurements from selected papers. The web extraction step was used to identify DNAzyme entries and database-linked publications that are relevant to DNAzyme-based nucleic-acid or bacterial RNA-related sensing.

DNAmoreDB was not treated as a direct LOD database. Instead, it was used in two stages:

1. **Candidate extraction:** extract algorithmically filtered DNAzyme candidates from the database. Data selection script - `extract_web_candidates.py`.
2. **Record selection:** select a small number of expert-relevant DNAzyme entries from the candidates and extract detailed database fields from their DNAmoreDB entry pages. Data selection script - `extract_web_records.py`.

The final web records were not selected by manually reviewing all sequences. First, the script generated candidates using general rules. Then, domain experts/biologists selected the most relevant entries from the candidate table for inclusion in `web_extracted_records.csv`.

## Page structure

DNAmoreDB contains several page types that were used in this practice.

### Home page

The home page provides general information about the database and its scope. It was used to document access conditions and the purpose of the source.

### Browse/search pages

The browse/search pages list DNAzyme entries in an HTML table-like layout. These pages include fields such as:

- DNAzyme name;
- sequence length;
- catalytic region;
- reaction type;
- metal ions or cofactors.

The search page can be used to inspect subsets of DNAzymes, for example RNA-related entries.

### API pages

The DNAmoreDB API provides structured JSON-like records. This is the most useful input for candidate extraction because it can be parsed more reproducibly than HTML tables.

The candidate extraction script uses the API/browse data to collect broad DNAzyme entries and apply relevance filters.

### Individual DNAzyme entry pages

Individual entry pages contain detailed information about one DNAzyme. These pages were used for final selected records.

For selected records, the script extracts fields such as:

- `Reaction`;
- `Reacting groups`;
- `Substrates`;
- `Product`;
- `Metal ion`;
- `Linkage`;
- `Seq description`;
- `Buffer conditions`;
- `Rate constant`, if present;
- `Notes`;
- `Catalytic region of the DNAzyme`;
- linked publication information.

The final selected records in `data/extracted/web_extracted_records.csv` were extracted from individual DNAmoreDB entry pages.

Access conditions

DNAmoreDB pages used in this practice are publicly accessible and do not require login, API keys, or institutional access.

The extraction scripts use polite simple HTTP requests. Raw downloaded pages are saved as snapshots under: data/raw/web/

## Extraction methods

The web extraction was implemented using Python scripts with `requests` and `BeautifulSoup`.

The extraction was split into two scripts:

| Script | Role |
|---|---|
| `scripts/extract_web_candidates.py` | Downloads DNAmoreDB API/search data and writes algorithmically filtered candidates to `web_extracted_candidates.csv` |
| `scripts/select_web_records.py` | Reads the candidate table, selects expert-approved records, downloads their DNAmoreDB entry pages, and extracts detailed entry fields into `web_extracted_records.csv` |
| `scripts/extract_web.py` | Wrapper script that runs the candidate extraction and record-selection steps in order |

### Candidate extraction rules

A DNAmoreDB entry was retained as a candidate if it matched general relevance rules, for example:

- reaction related to RNA cleavage;
- text contained RNA, rRNA, 16S, bacterial, *E. coli*, or related nucleic-acid/bacterial terms;
- text contained sensor-related terms such as detection, probe, fluorescent, fluorogenic, reporter, beacon, or assay;
- entry had database-linked publication metadata.

Catalytic values such as `kcat`, `kobs`, `kc`, or `yield` were extracted as optional metadata when available, but they were not used as the main inclusion criterion. 

### Record selection

After candidate extraction, the final records were selected by domain experts working on this topic.
the workflow was:
DNAmoreDB API/search pages
- algorithmic candidate extraction
- expert selection of relevant entries from candidates
- individual DNAmoreDB entry-page extraction
- web_extracted_records.csv

Rate limits and access notes

The script uses ordinary HTTP requests and saves downloaded snapshots under data/raw/web/. The extraction is small-scale and intended for educational use. No login, API key, or registration was required.

The script should be run responsibly with a low request volume. Raw snapshots are stored locally so that repeated parsing can be performed without repeatedly downloading the same pages.

## Extracted fields

The following DNAmoreDB fields are mapped into the web extraction schema

| DNAmoreDB page content | Dataset/output field |
|:----------------------|:---------------------|
| DNAzyme name | dnazyme_name |
| DNAmoreDB entry ID | dnazyme_id |
| Reaction | reaction |
| Reacting groups | reacting_groups |
| Substrates | substrates |
| Product | product |
| Metal ion / cofactor | metal_ion_or_cofactor |
| Linkage | linkage |
| Sequence description | seq_description |
| Buffer | buffer_conditions |
| Rate constant, if present | rate_constant |
| Notes | notes |
| Catalytic region | catalytic_region |
| Reported publication year | reported_publication_year |
| Reported publication first author | reported_publication_first_author |
| Reported publication last author / lab | reported_publication_lab_or_last_author |
| Reported publication title | reported_publication_title |
| PubMed ID | reported_publication_pmid |
| DOI | reported_publication_doi |
| Publication URL | reported_publication_url |
| Source page URL | source_url |
| Extraction method | extraction_method |
| Extraction confidence | extraction_confidence |

The final web records do not currently include LOD values because the selected DNAmoreDB entry pages provide DNAzyme metadata and linked publication information rather than direct sensor-performance LOD values. LOD extraction from linked papers is planned for later manual follow-up or Practice 5 refinement.

## Extraction problems

Extraction problems

Several extraction problems and limitations were identified.

1. DNAmoreDB is not a direct LOD database: DNAmoreDB mainly stores DNAzyme-core information, reaction details, substrates, catalytic regions, cofactors, and linked publications. It is not primarily a database of sensor-performance measurements such as LOD, linear range, or signal-to-background ratio.

2. Not all DNAzymes are sensors

3. HTML structure can vary: individual entry pages may format fields differently. Some values are present in text blocks, some in tables, and some in linked publication sections. The parser therefore uses field labels and fallback rules, but manual checking is still required for important records.

4. Linked publications require follow-up: DNAmoreDB provides publication links, PubMed IDs, and DOIs. These links are useful for follow-up extraction, but the current Practice 4 output only extracts values available directly on the DNAmoreDB pages. Detailed LOD values from linked papers will require manual extraction from the primary articles.

## Output files

- `data/extracted/web_extracted_records.csv` - this file contains the smaller set of selected DNAmoreDB records that were chosen from candidates by domain experts/biologists as directly relevant to the project topic
- `data/extracted/web_extracted_candidates.csv` - this file contains algorithmically selected candidate DNAmoreDB entries. The filtering is based on general relevance rules such as RNA cleavage, bacterial/RNA keywords, and sensing/detection keywords
- `data/raw/web/*.html` - snapshots
- `data/extracted/extraction_log.jsonl` 
