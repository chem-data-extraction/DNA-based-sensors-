# Practice 2 — Source map

> Document how you found sources and maintain `specs/source_map.json` as the machine-readable authority.

## Source search strategy

The source search focused only on DNA-based sensors for nucleic-acid detection 

Search platforms used:

- PubMed - biomedical literature and DOI verification
- Google Scholar - broad discovery of related papers
- Crossref / DOI landing pages - DOI and publication metadata verification
- Publisher websites - PLOS, ACS, GitHub, Kaggle
- DNAmoreDB — structured DNAzyme database for sequences, reaction conditions, cofactors, substrates, kinetic parameters, and literature links
- DNAzymeBuilder — web resource for RNA- and DNA-cleaving DNAzyme design and metadata
- Kolpashchikov lab publication list — topic-specific snowballing for BiDz, DNM, DNA minimachine, DNA nanomachine, and DNAzyme-cascade papers

Search keywords:

- "DNA sensors"
- "DNAzyme sensors"
- "sensor nucleic acid detection"
- "sensor 16S rRNA detection"
- "DNAzyme nanomachine nucleic acid detection"
- "DNAzyme nanomachine fluorogenic substrate delivery"
- "DNA nanomachines viral RNA detection"
- "DNAzyme cascade visual detection bacterial RNA"
- "DNAzyme machine selective sensitive detection DNA"
- "DNAmoreDB DNAzyme kinetic parameters substrate cofactor"
- "DNAzymeBuilder RNA DNA cleaving DNAzymes"
- "four-way junction sensor microRNA"

## Source groups

All sources are maintained in `specs/source_map.json`

### scientific_papers

| source_id | Source | Priority | Expected yield |
|---|---|---|---|
| paper_ateiah_2026_dnm | Ateiah et al. 2026, Analyst | 1 | DNM/BiDz performance, LODs for ssDNA, ssRNA, dsDNA amplicons, specificity, Gibbs-energy discussion |
| paper_hussein_2023_hdnm | Hussein et al. 2023, Analytical Chemistry | 1 | HDNM sensitivity, fluorogenic substrate delivery, LOD, sensor design |
| paper_solyanikova_2025_viral_rna_dnm | Solyanikova et al. 2025, IJMS | 1 | DNM detection of HPIV/RSV viral RNA, LOD, RNA target design |
| paper_kolpashchikov_2007_bidz | Kolpashchikov 2007, ChemBioChem | 2 | Foundational binary deoxyribozyme sensor |
| paper_gerasimova_2013_visual_bacterial_rna | Gerasimova et al. 2013, ChemBioChem | 2 | DNAzyme cascade for visual bacterial RNA detection |
| paper_cox_2016_mdm_rna | Cox et al. 2016, Chemical Communications | 2 | Multifunctional molecular DNA machine for RNA detection |
| paper_gerasimova_2013_16s_x_sensor | Gerasimova & Kolpashchikov 2013, Biosensors and Bioelectronics | 3 | LOD for E. coli 16S rRNA, X sensor architecture, RNA specificity |

### databases

The main database source is DNAmoreDB. It is not a sensor-performance database in the narrow sense, but it is highly relevant for web extraction and metadata enrichment because it stores DNAzyme sequence information, reaction conditions, substrates, metal-ion requirements, kinetic parameters, structural information, and publication links

### aggregators

Aggregators are used only for source discovery and snowballing, not as authoritative data sources

### github_repositories

No GitHub repository with directly reusable experimental data for this exact topic was found

### ml_datasets

No ML-ready dataset directly matching this topic was found. ML datasets or probe catalogs may be considered later only for predicted descriptors or candidate sequences, not for experimental performance records

## Priority sources

| Priority | source_id | Why |
|---|---|---|
| 1 | paper_ateiah_2026_dnm | open-access RSC paper; contains DNM/BiDz performance for ssDNA, ssRNA, and dsDNA targets |
| 1 | paper_hussein_2023_hdnm | Direct DNAzyme nanomachine sensitivity paper with supplementary/figshare materials |
| 1 | paper_solyanikova_2025_viral_rna_dnm | Direct viral RNA DNM detection paper; open access; relevant for RNA target coverage |
| 1 | db_dnamoredb | Best structured web/API source for DNAzyme metadata, reaction conditions, cofactors, and kinetic descriptors |
| 2 | db_dnazymebuilder | Useful for catalytic-core metadata and DNAzyme design descriptors |
| 2 | paper_kolpashchikov_2007_bidz | Foundational BiDz paper for binary deoxyribozyme nucleic-acid analysis |
| 2 | paper_cox_2016_mdm_rna | Important DNA machine paper for RNA detection |
| 2 | paper_lyalina_2019_dna_minimachine | Important DNA machine paper for selective DNA detection |
| 3 | paper_bone_2014_doc | Useful DNAzyme cascade amplification source, but less directly nucleic-acid-target-specific |
| 3 | paper_gerasimova_2013_16s_x_sensor | Direct RNA-target example; reports LOD for E. coli 16S rRNA |

## Access conditions

| source_id | Access status | Access method | Notes |
|---|---|---|---|
| paper_ateiah_2026_dnm | open_access | RSC HTML/PDF | RSC page states Open Access and CC BY-NC 3.0 license |
| paper_hussein_2023_hdnm | publisher_page / supplementary available | ACS HTML/PDF + ACS Figshare | Main text may depend on access; supplementary collection is available |
| paper_solyanikova_2025_viral_rna_dnm | open_access | MDPI HTML/PDF | Direct web extraction possible |
| db_dnamoredb | open_access | HTML + API/CSV | No login required; cite DNAmoreDB paper and linked primary papers |
| db_dnazymebuilder | open_access | web tool | Use for metadata/design descriptors, not unverified predicted performance |
| paper_gerasimova_2013_16s_x_sensor | abstract_open / full text may require publisher or repository access | PubMed, ScienceDirect, PMC/institutional access if available | Use abstract for metadata; full extraction requires PDF |

## Expected data types

| Source group | Expected data types |
|---|---|
| scientific_papers | PDF text, HTML full text, tables, figures, figure captions |
| supplementary_materials | supplementary PDFs, sequence tables, raw/processed fluorescence data, assay protocols |
| databases | HTML tables, API JSON, CSV exports |
| aggregators | DOI, PMID, title, authors, abstracts, metadata |
| github_repositories | none confirmed |
| ml_datasets | none confirmed |

## Expected conflicts and overlaps

| Overlap / conflict | Sources | Resolution rule |
|---|---|---|
| Same DNAzyme appears in DNAmoreDB and a primary paper | Use the primary paper for sensor-performance values; use DNAmoreDB for catalytic metadata, reaction type, cofactors, and publication links |
| Main text and supplementary file report the same value | Prefer supplementary tables for exact values; use main text for interpretation |
| Review article reports a value from a primary paper | Use the primary paper whenever available; reviews are source-discovery/context only |
| Same sensor tested under different temperature, buffer, incubation time, or metal-ion concentration | Store as separate records |
| kobs and LOD reported for the same DNAzyme system | Store as separate records because they describe different measurement types |
| Values only visible in figures | Extract manually or with digitization and mark extraction_confidence as medium/low |
| Range values such as 5–10 pM | Preserve range; do not silently use midpoint unless documented |

## Coverage gaps

| Gap | Reason | Plan |
|---|---|---|
| No large structured database | This topic is mostly represented by individual experimental papers, not centralized databases | Build v0.1.0 from primary papers and supplementary files |
| Small number of directly relevant papers | SNP/SNV-specific multicomponent DNA sensors are a narrow research area | Use snowballing from Kolpashchikov lab papers and citation networks |
| Many values are in plots | Fluorescence ratios, melting curves, and discrimination profiles are often plotted, not tabulated | Use manual extraction or figure digitization and record extraction confidence |
| Supplementary files required for sequences | Main papers often describe sensor labels but put full sequences in SI | Extract SI early, before final dataset construction |
| RNA target coverage is lower than DNA model target coverage | Many studies use synthetic DNA targets first | Mark synthetic DNA models separately and prioritize RNA-target papers such as 16S rRNA and miRNA sensors |
| DNAzyme sensors have heterogeneous readouts | Fluorescence, chemiluminescence, colorimetric, electrochemical readouts are not directly comparable | Keep transduction_method, measurement_type, and assay conditions explicit |
