# Practice 2 — Source map

> Document how you found sources and maintain `specs/source_map.json` as the machine-readable authority.

## Source search strategy

The source search focused only on DNA-based sensors for nucleic-acid detection and SNP/SNV discrimination

Search platforms used:

- PubMed - biomedical literature and DOI verification
- Google Scholar - broad discovery of related papers
- Crossref / DOI landing pages - DOI and publication metadata verification
- Publisher websites - PLOS, ACS, Wiley, Elsevier, Springer
- Kolpashchikov lab publication list - snowballing source for related OC, X, binary, tricomponent, and Owl sensor papers

Search keywords:

- "DNA sensor SNP discrimination universal molecular beacon"
- "operating cooperatively sensor nucleic acid recognition"
- "molecular beacon based X sensor 16S rRNA"
- "tricomponent probe SNP folded nucleic acids"
- "Owl sensor single nucleotide variation"
- "binary DNA probe highly specific nucleic acid recognition"
- "four-way junction sensor microRNA"
- "DNA hybridization probe single nucleotide mismatch fluorescence"

## Source groups

All sources are maintained in `specs/source_map.json`

### scientific_papers

| source_id | Source | Type | Priority | Expected yield |
|---|---|---|---|---|
| paper_cornett_2013_oc_sensor | Cornett et al. 2013, PLOS ONE, OC sensor | primary research article | 1 | LOD, SNP selectivity, signal-to-noise, rs87T/rs87C, E. coli 16S rRNA |
| paper_gerasimova_2013_16s_x_sensor | Gerasimova & Kolpashchikov 2013, Biosensors and Bioelectronics | primary research article | 1 | LOD for E. coli 16S rRNA, X sensor architecture, RNA specificity |
| paper_nguyen_2011_tricomponent | Nguyen et al. 2011, Chemistry — A European Journal | primary research article | 1 | tricomponent probe, folded nucleic acids, SNP discrimination, LOD range |
| paper_stancescu_2016_nonequilibrium_x | Stancescu et al. 2016, JACS | primary research article | 1 | X probe, point mutation discrimination, Fm/Fmm, ΔT1.5, temperature range |
| paper_karadeema_2018_owl | Karadeema et al. 2018, Nanoscale | primary research article | 1 | Owl sensor, DNA/RNA analytes, SNV discrimination, 5–32 °C range |
| paper_kolpashchikov_2006_binary | Kolpashchikov 2006, JACS | primary research article | 2 | binary DNA probe, single-base mismatch discrimination |
| paper_grimes_2010_realtime_snp | Grimes et al. 2010, Angewandte Chemie | primary research article | 2 | real-time SNP analysis in folded nucleic acids |
| paper_labib_2013_4j_mirna | Labib et al. 2013, Analytical Chemistry | primary research article | 3 | 4-way-junction electrochemical miRNA sensor; useful for broader nucleic-acid detection |

### databases

No structured public database was found that directly stores experimental performance measurements for DNA-based SNP/SNV nucleic-acid sensors

### aggregators

Aggregators are used only for source discovery and snowballing, not as authoritative data sources

### github_repositories

No GitHub repository with directly reusable experimental data for this exact topic was found

### ml_datasets

No ML-ready dataset directly matching this topic was found. ML datasets or probe catalogs may be considered later only for predicted descriptors or candidate sequences, not for experimental performance records

## Priority sources

| Priority | source_id | Why |
|---|---|---|
| 1 | paper_cornett_2013_oc_sensor | Directly matches SNP-specific DNA sensor topic; contains LOD and selectivity data |
| 1 | paper_gerasimova_2013_16s_x_sensor | Direct RNA-target example; reports LOD for E. coli 16S rRNA |
| 1 | paper_nguyen_2011_tricomponent | Directly relevant f/m strand tricomponent probe for SNP analysis in folded nucleic acids |
| 1 | paper_stancescu_2016_nonequilibrium_x | Key X-probe paper for broad temperature-range point-mutation discrimination |
| 1 | paper_karadeema_2018_owl | Key Owl-sensor paper for DNA/RNA SNV discrimination and 4WJ-like architecture |
| 2 | paper_kolpashchikov_2006_binary | Earlier binary DNA probe; useful for historical baseline and mismatch discrimination |
| 2 | paper_grimes_2010_realtime_snp | Direct SNP detection in folded nucleic acids; useful baseline for real-time detection |
| 3 | paper_labib_2013_4j_mirna | Direct 4WJ nucleic-acid sensor, but not SNP/SNV-specific. Lower priority |

## Access conditions

| source_id | Access status | Access method | Notes |
|---|---|---|---|---|
| paper_cornett_2013_oc_sensor | open_access | publisher HTML / PDF | - |
| paper_gerasimova_2013_16s_x_sensor | abstract_open / full text may require publisher or repository access | PubMed, ScienceDirect, PMC/institutional access if available | Use abstract for metadata; full extraction requires PDF |
| paper_nguyen_2011_tricomponent | open full text available through PMC / publisher metadata | PMC / Wiley page | Suitable for direct extraction |
| paper_stancescu_2016_nonequilibrium_x | publisher access / author version / uploaded PDF | ACS / PubMed / institutional PDF | Full extraction from PDF and supplementary information |
| paper_karadeema_2018_owl | author-version PDF available / publisher landing page | RSC PDF / publisher page | Suitable for direct extraction from PDF and SI |
| paper_kolpashchikov_2006_binary | publisher access / PubMed metadata | ACS / PubMed | Full extraction may require institutional access |
| paper_grimes_2010_realtime_snp | publisher access / PubMed metadata | Wiley / PubMed | Full extraction may require institutional access |
| paper_labib_2013_4j_mirna | publisher access / PubMed metadata | ACS / PubMed | Lower priority because target is miRNA, not SNP/SNV |


## Expected data types

| source_id | Expected data type | Format | Fields likely available |
|---|---|---|---|
| paper_cornett_2013_oc_sensor | article text, figures, supplementary data | HTML/PDF/SI | sensor_architecture, target_name, target_sequence, measurement_type, LOD, signal_to_noise, buffer, temperature, MgCl2 |
| paper_gerasimova_2013_16s_x_sensor | article text, figures, supplementary data | PDF/SI | X sensor design, RNA target, LOD, specificity, reporter probe, adapter strands |
| paper_nguyen_2011_tricomponent | article text, tables, supplementary sequences | HTML/PDF/SI | f-strand, m-strand, target sequence, LOD, folded target conditions |
| paper_stancescu_2016_nonequilibrium_x | article text, figures, supplementary tables | PDF/SI | X probe variants, m-arm length, Fm/Fmm, ΔT1.5, temperature range |
| paper_karadeema_2018_owl | article text, figures, supplementary sequences | PDF/SI | Owl sensor R/P/UMB sequences, DNA/RNA targets, SNV discrimination, temperature range |
| paper_kolpashchikov_2006_binary | article text and figures | PDF | binary probe design, mismatch discrimination, signal response |
| paper_grimes_2010_realtime_snp | article text and figures | PDF | real-time SNP response, folded nucleic acid target, signal metrics |
| paper_labib_2013_4j_mirna | article text, figures, electrochemical data | PDF/SI | miRNA target, 4WJ sensor, LOD, linear range, electrochemical method |

## Expected conflicts and overlaps

| Overlap / conflict | Sources | Resolution rule |
|---|---|---|
| Same sensor described in primary paper and protocol chapter | paper_cornett_2013_oc_sensor, Methods Mol Biol protocol papers | Primary research article wins for quantitative values; protocol used only for design details |
| Same UMB-based design family appears across OC, X, tricomponent, and Owl papers | Cornett 2013, Gerasimova 2013, Nguyen 2011, Stancescu 2016, Karadeema 2018 | Keep records separate by `sensor_architecture`, `sensor_id`, target, and measurement type |
| Values are shown only in figures, not tables | most primary papers | Store as `figure_digitized` or `pdf_manual`; set `extraction_confidence = medium` unless exact values are printed |
| Same performance metric reported as approximate in text and exact in table | paper text + table | Table or SI value wins; text value stored only in notes. |
| Different sources report performance under different buffer or temperature conditions | any | Do not average. Keep separate records because assay conditions affect hybridization specificity |
| DNA model target vs real RNA target | Nguyen 2011, Gerasimova 2013, Owl paper | Use `target_type` to separate DNA, RNA, synthetic_DNA_model, and synthetic_RNA_model |

## Coverage gaps

| Gap | Reason | Plan |
|---|---|---|
| No large structured database | This topic is mostly represented by individual experimental papers, not centralized databases | Build v0.1.0 from primary papers and supplementary files |
| Small number of directly relevant papers | SNP/SNV-specific multicomponent DNA sensors are a narrow research area | Use snowballing from Kolpashchikov lab papers and citation networks |
| Many values are in plots | Fluorescence ratios, melting curves, and discrimination profiles are often plotted, not tabulated | Use manual extraction or figure digitization and record extraction confidence |
| Supplementary files required for sequences | Main papers often describe sensor labels but put full sequences in SI | Extract SI early, before final dataset construction |
| RNA target coverage is lower than DNA model target coverage | Many studies use synthetic DNA targets first | Mark synthetic DNA models separately and prioritize RNA-target papers such as 16S rRNA and miRNA sensors |
