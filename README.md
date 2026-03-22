> **Start here →** [`analysis/complete-findings-english.md`](analysis/complete-findings-english.md) — the single document presenting all verified results.

# Epstein Files Transparency Act — Primary Source Analysis

An AI-assisted analysis of 4,251 documents released under the Epstein Files Transparency Act (H.R. 4405) in January 2026, cross-referenced against a 2.89-million-page corpus and 165+ existing reports. Directed by Adrian Moen. Analysis and writing by Claude (Anthropic).

**What you can verify:** Every finding cites specific EFTA document numbers. The documents are public at [justice.gov/epstein](https://www.justice.gov/epstein). 56/56 citations independently verified against rhowardstone's full-text corpus with zero errors.

---

## What This Found

Findings from SDNY prosecution memoranda. Most have also been documented by [rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research) (165+ reports). What this repo adds: page-level PDF verification, complete proffer mapping, financial deconstruction, network graph analysis, and five genuinely new findings verified against all public sources.

**Genuinely new (verified March 22, 2026):**

1. **No client accounts** — SDNY reviewed three banks and found no evidence of Epstein managing anyone else's money. "We have not identified any accounts that are consistent with Epstein handling or investing other people's money." Source: EFTA02731148. Not in any other EFTA project.

2. **78 proffer agreements mapped** — Complete proffer landscape across the full corpus. SDNY conducted dozens of formal interview sessions. One indictment (Maxwell). No other project has this count.

3. **18 redacted pages structural skeleton** — Pages 68-85 of the prosecution memo are covered by redaction bars, but surviving section headings reveal five charging analysis sections (A through E). Page 75: "Leslie Groff **and/or** Ghislaine Maxwell with a federal crime." Section A is 8 pages — the longest analysis — for a redacted person.

4. **Groff proffer agreement** (EFTA01682023) — Formal proffer dated July 23, 2021, with attorney Michael Bachner. Her cooperation is publicly known; this specific document is not cited elsewhere.

5. **Linguistic hedging predicts non-charging** — SDNY uses hedging language for people it didn't charge and confident language for Maxwell. The pattern is consistent across all 22 tracked persons.

**Note:** SDNY's memo states they were unable to corroborate the "lent out" accounts — specific allegations about Dubin, Black, Staley, Andrew, and Weinstein remain uncorroborated in the memo's own assessment. The victim's recruitment by Maxwell, abuse by Epstein, and recruiting of minors were corroborated.

---

## Documents

| File | Description |
|------|-------------|
| **`analysis/complete-findings-english.md`** | **Start here.** All verified results in one document. |
| `analysis/epstein-financial-deconstruction-english.md` | No client accounts + Wexner proffer + Deutsche Bank review. Every quote verbatim from OCR. |
| `analysis/epstein-financial-deconstruction-norwegian.md` | Norwegian version of the financial deconstruction. |
| `analysis/groff-investigation-english.md` | Leslie Groff: 50 memo mentions, scheduling emails from corpus, proffer agreement. |
| `analysis/groff-prosecution-gap-english.md` | Four explanations for why Groff was never charged, tested against corpus data. |
| `analysis/proffer-landscape-english.md` | 78 proffers mapped. SDNY interviewed everyone and charged one person. |
| `analysis/victim-cross-reference-english.md` | Victim designations mapped across volumes. No real names. |
| `analysis/epstein-v4-english.md` | Earlier analysis (v4). Superseded by complete-findings but preserved for record. |
| `analysis/epstein-v4-norwegian.md` | Norwegian original of v4. |
| `analysis/epstein-findings-english.md` | Detailed findings report. Superseded by complete-findings. |
| `analysis/epstein-findings-norwegian.md` | Norwegian original of the findings report. |

## Source Data

OCR text files in `ocr/` (~6.8 MB, 18 files). See `ocr/README.md` for the off-by-one EFTA marker rule.

    grep -A 20 'EFTA02731138' ocr/epstein_ren16.txt  # Returns content of page EFTA02731139

## Tools

See [`tools/README.md`](tools/README.md) for full documentation. Key tools:

- **Verification** (`tools/verification/`) — QA checks, PDF page verification, citation validation
- **Unified knowledge base** (`tools/unified/`) — 22-person database with evidence scores, graph analysis, proffer landscape, solve map, and queryable red thread
- **Pattern analysis** (`tools/analysis_outputs/`) — Financial trails, leads, redaction analysis
- **Entity network** (`tools/entity_network/`) — SpaCy NER with 6 noise filters

## How to Verify

1. Open any EFTA number at [justice.gov/epstein](https://www.justice.gov/epstein)
2. Compare against our citation
3. If wrong, open an issue

## Related Work

- **[rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research)** — 165+ forensic reports, 1,614-person registry. Most comprehensive EFTA analysis available. Most of our findings independently confirmed there.
- **[rhowardstone/Epstein-research-data](https://github.com/rhowardstone/Epstein-research-data)** — Full-text corpus (2.89M pages), knowledge graph, person registry.

## Author

Adrian Moen · Fredrikstad, Norway · Analysis directed by Adrian, executed and written by Claude (Anthropic).

## License

Public domain.
