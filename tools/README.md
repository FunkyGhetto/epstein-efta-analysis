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
- `entities.json` (2.5 MB) — 356 unique names with every occurrence, EFTA page, and full context
- `entities_compact.json` (950 KB) — same data with context trimmed to 50 chars for faster loading
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

## Verification Scripts (`verification/`)

**`verification/find_correct_efta.py`** — Extracts text from every page of a PDF independently (not from OCR files) and searches for key phrases. Used to discover and correct the off-by-one error in OCR-derived EFTA numbers.

**`verification/final_verify.py`** — Checks every EFTA number cited in the repo against actual PDF text. The sign-off script that confirmed all 16 key citations are correct. Output: 16/16 verified, 0 failures.

**`verification/qa_check.py`** — Automated quality assurance script that validates the entire repo. Checks EFTA number consistency, cross-file consistency, link validation, claim consistency, Norwegian-English parity, source line completeness, and forbidden patterns. Run after any changes:

    python3 tools/verification/qa_check.py

---

## Pattern Analysis (`analysis_outputs/`)

Three automated analyses of the OCR text. Scripts are in `analysis_outputs/scripts/`, output data in `analysis_outputs/data/`.

**Money Trail** (`scripts/money_trail.py`) — Extracts dollar amounts with dates, payers, and recipients from all OCR files. Found 605 financial references, 180 in prosecution memos. Key pattern: $250K wire in December 2018 (Kahn→victim via Groff, 6 months before arrest), $100K after Miami Herald coverage, and Leon Black's $158M+ in tax advisory payments to Epstein over 2012–2017. Output: `data/money_trail.json`, `data/money_trail.txt`.

**Phone Patterns** (`scripts/phone_patterns.py`) — Extracts phone numbers from CDR-containing files. Found 206 unique numbers. Most are institutional (court reporting, account services). Identified LSJE LLC numbers (340-775-8100/8108, Epstein's USVI company) and Palm Beach area code concentration (561). Output: `data/phone_patterns.json`, `data/phone_patterns.txt`.

**Redaction Analysis** (`scripts/redaction_analysis.py`) — Maps redaction patterns in prosecution memos. Found 2,235 redaction instances. Mapped fragments to victim identifiers: Victim-1 (35 instances, NY recruitment), Victim-2 (30 instances, FL recruitment), Victim-3 (11, paid $200/visit), Victim-4 (6, single incident). Output: `data/redaction_analysis.json`, `data/redaction_analysis.txt`.

**Financial Evidence** (`data/financial_evidence.txt`) — Complete evidence extraction for the financial deconstruction analysis, with OCR line numbers and EFTA markers.

**Victim Profiles** (`data/victim_profiles.json`) — Structured victim contextual fingerprints from the cross-volume analysis.

**Lead Finder** (`scripts/find_leads.py`) — Systematically identifies unresolved threads, contradictions, unexplored people, uncited financial transactions, cross-reference gaps with rhowardstone, and uncovered victim sections. Found 537 leads: 48 high, 124 medium, 365 low priority. Output: `data/leads.json`, `data/leads.txt`. Note: unexplored person results include false positives from the massage textbook OCR; the high-priority victim and financial leads are the most actionable.

    python3 tools/analysis_outputs/scripts/find_leads.py

---

## Unified Knowledge Base (`unified/`)

Consolidates every data source — entity network, financial trail, linguistic patterns, co-absence, temporal proximity, redaction bridges, victim connections, leads, rhowardstone cross-reference — into one queryable knowledge base per person.

**`unified/build_knowledge_base.py`** — Builds `knowledge_base.json` from all analysis outputs. Requires the full-text corpus database for corpus counts.

**`unified/query.py`** — Command-line query tool:

    python3 tools/unified/query.py --person "Leslie Groff"    # Everything about one person
    python3 tools/unified/query.py --compare "Leslie Groff" "Sarah Kellen"  # Side by side
    python3 tools/unified/query.py --pattern hedging           # Linguistic patterns
    python3 tools/unified/query.py --absent                    # Absent from memo
    python3 tools/unified/query.py --uncharged                 # Evidence but no charges
    python3 tools/unified/query.py --red-thread                # The full narrative

**`unified/knowledge_base.json`** — 22 persons with evidence scores, action scores, and gap analysis.

**`unified/rebuild.py`** — Automated full rebuild of the entire project state from raw data. Connects to the corpus, reads all JSONs, greps OCR/rhowardstone, and regenerates knowledge_base.json, solve_map.json, and project_state.json.

    python3 tools/unified/rebuild.py

**`unified/solve_status.py`** — Prints the solve dashboard: 73 questions scored across 5 categories (identity, decision, financial, structural, connection), overall percentage, top unsolved, and walls.

    python3 tools/unified/solve_status.py

**Additional data in `unified/`:**
- `graph_analysis.json` — Network graph metrics: betweenness, eigenvector, PageRank, community detection, structural holes
- `cooccurrence_matrix.json` — Fresh 231-pair co-occurrence matrix from corpus (222 non-zero pairs)
- `proffer_landscape.json` — All 78 proffer agreements with dates, attorneys, and terms
- `proffer_identifications.json` — Attempted identification of 71 redacted profferors
- `investigation_timeline.json` — Complete chronological timeline (43 events)
- `hole_geometry.json` — 18 holes clustered by shape similarity
- `triangulation_results.json` — Cross-question inference chains
- `dimensional_analysis.json` — Redaction shapes, filing topology, temporal rhythm, linguistic fingerprints, negative space
- `internet_probe_results.json` — Cross-reference of findings against public sources
- `micro_search_results.json` — Surgical internet probes on every data point
- `excised_pages_analysis.txt` — Structural mapping of 18 redacted charging analysis pages (CORRECTION: redacted, not excised)
- `project_state.json` — Current project state snapshot
- `probe_results/` — Deep probe data for Groff, Wexner, Black, and Emmy Tayler
