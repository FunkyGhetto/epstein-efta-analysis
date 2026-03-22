# Tools

These tools were built during the analysis to verify citations and extract entity data. They require local files to run and are included to document the verification process, not to work out of the box.

---

## EFTA Verifier (`verifier/`)

A native macOS desktop app that renders original PDF pages alongside OCR text for side-by-side comparison.

**What it does:**
- Takes one or more EFTA document numbers as input
- Finds the correct PDF across all 8 volumes (2,093 PDFs)
- Renders the page as an image next to the corresponding OCR text
- Supports delta-encoded search strings for sharing specific page sets
- Exports results as a ZIP with page images and text files

**Requirements:**
- macOS (uses Quartz for PDF rendering)
- Python 3 with: `pywebview`, `pypdf`
- A local copy of the EFTA PDF documents, organized as:
  ```
  ~/Documents/Epstein Files Transparency Act (H.R.4405)/
    PDF-dokumenter/
      VOL00001/IMAGES/0001/*.pdf
      ...
      VOL00012/IMAGES/0001/*.pdf
  ```

**To use with a different PDF location**, edit the `PDF_BASE` path near the top of `app.py`.

**Run:** `python3 tools/verifier/app.py`

---

## Entity Network (`entity_network/`)

SpaCy-based named entity extraction across all 18 OCR files.

**What it does:**
- Processes ~6.8 MB of OCR text with the `en_core_web_lg` model
- Applies 6 noise filters to remove non-document content
- Builds a co-occurrence matrix (names sharing EFTA pages)
- Flags names by proximity to keywords: massage, minor, sexual, abuse, recruit, payment, rape

**Noise filters:**
1. **EFTA proximity** — only counts names within 1,000 characters of an EFTA page marker, eliminating seized textbooks and non-document content
2. **OCR artifact removal** — discards fragments like "ia", "iz", "stein" that SpaCy misidentifies
3. **Header/footer removal** — discards text that repeats identically more than 20 times
4. **Legal citation removal** — excludes names after "v." (case citations)
5. **Alias deduplication** — merges name variants with auto-merge for short names co-occurring 60%+ with a full name
6. **Single-occurrence removal** — names appearing only once are treated as noise

**Output** (committed in `data/`):
- `entities.json` — 356 unique names with every occurrence, EFTA page, and context
- `cooccurrence.json` — 809 name pairs sharing EFTA pages, with page lists
- `flagged.json` — 65 names ranked by keyword proximity score

**`viewer.py`** is a native desktop app (pywebview) for browsing the results — searchable name list, connections panel, keyword flags, dossier export.

**Requirements:**
- Python 3 with: `spacy`, `pywebview`
- SpaCy model: `python3 -m spacy download en_core_web_lg`
- Local OCR files in `ocr/` (included in the repo)

**Run extraction:** `python3 tools/entity_network/extract.py`
**Run viewer:** `python3 tools/entity_network/viewer.py`

---

## Citation Scripts

**`find_correct_efta.py`** — Extracts text from every page of a PDF independently (not from OCR files) and searches for key phrases. Used to discover and correct the off-by-one error in OCR-derived EFTA numbers.

**`final_verify.py`** — Checks every EFTA number cited in the repo against actual PDF text. The sign-off script that confirmed all 16 key citations are correct. Output: 16/16 verified, 0 failures.
