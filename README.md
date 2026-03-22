# Epstein Files Transparency Act — Primary Source Analysis

An AI-assisted analysis of 4,251 documents released under the Epstein Files Transparency Act (H.R. 4405) in January 2026. Directed by Adrian Moen. Searching, analysis, and writing performed by Claude (Anthropic).

## How This Was Made

I (Adrian) OCR-processed 4,251 PDF files from the EFTA release using Tesseract. I then gave the resulting text files to Claude and directed the analysis through conversation — asking questions, choosing which threads to follow, and deciding what mattered. Claude performed the actual searching, identified the key passages, built the network analysis, cross-referenced documents, and wrote every word of text you see in this repo. I reviewed the flagged passages and Claude's conclusions, but I did not read the 7,700 pages of OCR output myself.

This is not an analysis I wrote with AI assistance. It is an analysis AI performed at my direction. The distinction matters because I'd rather you judge the work on whether it's correct than on who — or what — produced it.

**What you can verify right now:** Every finding cites specific EFTA document numbers. The documents are public. You can look them up. If the analysis says EFTA02731139 contains Maxwell instructing a victim to perform sexual acts on Glen Dubin, you can check whether EFTA02731139 says that. If it doesn't, the analysis is wrong. If it does, then the question of what tool produced it is irrelevant.

The prosecution memos in VOL00012 — marked "Attorney Work Product" and "Subject to Fed. R. Crim. P. 6(e)" — are the most substantive documents in the entire release. They are also the ones almost nobody has read, because reading 18 files of OCR output is not something journalists on deadline do.

---

## What This Found

Findings from SDNY prosecution memoranda, independently verified against original PDF pages. Most of these findings have also been documented by the comprehensive [rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research) project (165+ reports, 1,614-person registry). What this repo adds is page-level PDF verification of every citation and a reproducible method accessible to non-technical users. One finding — the absence of client accounts — appears to be genuinely new.

- **Glen Dubin** — Maxwell explicitly instructed a victim to perform sexual acts on him. Named in SDNY memo EFTA02731139. The victim's name is redacted. The account may be Giuffre's (who has publicly accused Dubin in civil proceedings) or a separate victim — the redaction prevents confirmation. Either way, this is SDNY's internal prosecution memo documenting the testimony as part of their case preparation. No law enforcement action followed. *(Independently confirmed by rhowardstone/Epstein-research from the same source document.)*

- **Harvey Weinstein** — Epstein instructed a victim to massage Weinstein at the Paris residence. Weinstein ordered her to remove her shirt. She refused. Source: EFTA02731096. Not previously reported from primary EFTA documents. *(Independently confirmed.)*

- **Leon Black** — Subject of an active federal human trafficking referral in June 2023 (EFTA02731477), with an identified minor victim. This goes beyond the civil lawsuits that have been publicly reported. *(Independently confirmed; their project includes additional DANY interview data.)*

- **"Cooperating Defendants: None"** — SDNY's memo (EFTA02731053) explicitly states they had zero cooperating defendants and planned to use Epstein's indictment as leverage. His death eliminated this strategy. This is the structural explanation for why no co-conspirators were indicted. *(Independently confirmed from a different source document.)*

- **No cameras in bedrooms** — The memo explicitly states searches "did not reveal any cameras in any of the bedrooms or massage rooms." The blackmail narrative is not supported by the physical evidence found during the 2019 searches. Source: EFTA02731148. *(Independently confirmed from a different source: FBI CID summary EFTA00038617.)*

- **No client accounts** — "We have not identified any accounts that are consistent with Epstein handling or investing other people's money." The hedge fund manager myth is disproven in SDNY's own words. Source: EFTA02731148. **(Not found in any other EFTA analysis project. Appears to be a genuinely new finding.)**

- **Darren Indyke** (Epstein's attorney) told a witness not to talk to police (EFTA02731123) and brought computers into prison for Epstein to have video sex (EFTA02731127). *(Independently confirmed; rhowardstone includes a congressional witness brief on Indyke.)*

- **David Blaine** introduced a victim to Epstein at a NYC nightclub. Source: EFTA02731111. *(Listed in their registry but with minimal analysis. Our SDNY memo context adds detail.)*

- **Leslie Groff** was still actively recruiting in December 2018, six months before Epstein's arrest, and was never indicted despite being named throughout the prosecution memo. Source: EFTA02731133. *(Partially confirmed; their focus is different. The $250K wire context appears new.)*

---

## Documents

| File | Description |
|------|-------------|
| `analysis/epstein-v4-english.md` | Complete analysis (~2,400 words). All findings integrated with four evidence levels. |
| `analysis/epstein-findings-english.md` | Detailed findings report (~4,500 words). Full EFTA sourcing, redaction analysis, identity reconstruction. |
| `analysis/epstein-v4-norwegian.md` | Norwegian original of v4. |
| `analysis/epstein-findings-norwegian.md` | Norwegian original of the findings report. |

## Source Data

The raw OCR text files are included in the `ocr/` folder (~6.8 MB, 18 files). You can verify any finding by grepping for the EFTA document number in the OCR files. See `ocr/README.md` for how EFTA page markers work in the OCR output.

Example:

    grep -A 20 'EFTA02731138' ocr/epstein_ren16.txt

This returns the content of page EFTA02731139 (the Dubin page). See `ocr/README.md` for why you grep for the number one below.

No need to download 4,251 PDFs or run OCR yourself.

## Tools

Two tools were built during this analysis and are included in `tools/`. Neither is meant to work out of the box — they are included to document the verification process. See `tools/README.md` for setup details.

**EFTA Verifier** (`tools/verifier/`) — Renders any EFTA page from the original PDFs side-by-side with the corresponding OCR text. Used to visually verify every citation in this repo. Requires local EFTA PDF files.

**Entity Network** (`tools/entity_network/`) — SpaCy NER extraction across all 18 OCR files with 6 noise filters. Identified 356 unique person names, 809 co-occurrence pairs, and 65 names flagged by keyword proximity. The network confirms the manual analysis: Maxwell↔Epstein is the strongest connection (141 shared pages), followed by Epstein↔Black (47) and Epstein↔Groff (26). Filtered JSON data is included in `tools/entity_network/data/`.

## Method

**Phase 1 — OCR:** Adrian processed 4,251 PDF files with Tesseract 4.1.1 (200 DPI, English). Output: ~6.8 MB cleaned text, 18 files.

**Phase 2 — Verification:** Claude compared findings against 814 public sources.

**Phase 3 — Systematic analysis:** Claude performed grep searches, Python co-occurrence mapping, date extraction, and identified key passages. Adrian directed which questions to ask and which threads to follow.

**All text in this repo was written by Claude.** Adrian directed the analysis, reviewed the results, and made editorial decisions.

## How to Verify

1. Access the EFTA documents from the public release at https://www.justice.gov/epstein/
2. Look up any EFTA number cited in the analysis
3. Read the document
4. Decide for yourself

If you find an error, open an issue. If you find something missed, open a pull request.

## Related Work

This analysis exists alongside significantly larger projects analyzing the same documents:

- **[rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research)** — 165+ forensic reports, 1,614-person entity registry, 273 pseudonym identifications, congressional witness briefs. The most comprehensive EFTA analysis available. Most of our findings are independently confirmed there.
- **[rhowardstone/Epstein-research-data](https://github.com/rhowardstone/Epstein-research-data)** — Companion data repo: persons registry, knowledge graph, phone number enrichment, DOJ document removal audit.

What this repo contributes that the above do not:
1. **"No client accounts"** — The finding that SDNY found no evidence of Epstein handling other people's money (EFTA02731148) does not appear in any of the above projects.
2. **Page-level PDF verification** — Every EFTA citation was verified by rendering the original PDF page and comparing it to OCR text. The off-by-one OCR marker issue was discovered and corrected during this process.
3. **Accessible method** — OCR + AI-directed search + visual verification, documented end-to-end, reproducible by anyone with Tesseract and a chat interface.

## Author

Adrian Moen. Fredrikstad, Norway. No journalistic or academic affiliation. Analysis directed by Adrian, executed and written by Claude (Anthropic).

## License

Public domain.
