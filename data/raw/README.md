# Raw data

Store **unaltered** source files here. Do not edit files in this folder after download; add new versions with clear names instead.

## What belongs here

| Subfolder | Contents |
|-----------|----------|
| `pdf/` | Original PDF papers and supplementary files referenced in `specs/pdf_extraction_manifest.json` |
| `web/` | HTML snapshots, saved pages, or API JSON responses referenced in `specs/web_extraction_manifest.json` |
| `external/` | Third-party CSV, ZIP, or database exports (with license notes in `specs/source_map.json`) |

## What does not belong here

- Cleaned or merged tables (use `data/interim/` or `data/processed/`)
- Extracted record CSVs (use `data/extracted/`)

Document each file’s `source_id`, download date, and license in your source map and practice reports.

# Raw PDF files

Put the original, unmodified PDFs here before running `scripts/extract_pdf.py`.

Expected filenames for the current Practice 3 manifest:

- `nihms534513.pdf` — Gerasimova et al. 2013, Deoxyribozyme cascade for visual detection of bacterial RNA
- `nihms912297.pdf` — Cox et al. 2016, Multifunctional molecular DNA machine for RNA detection
- `ijms-26-03652.pdf` — Solyanikova et al. 2025, Multicomponent DNA Nanomachines for Amplification-Free Viral RNA Detection

Do not edit raw PDFs after download/upload. If a file changes, save a new version with a clear filename and update `specs/pdf_extraction_manifest.json`.
