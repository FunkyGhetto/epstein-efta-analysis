# Epstein Files Transparency Act — Primary Source Analysis

An independent analysis of 4,251 documents released under the Epstein Files Transparency Act (H.R. 4405) in January 2026.

## Before You Dismiss This

Yes, AI tools were used. Here's what that means and what it doesn't.

**What the AI did:** OCR processing, text search across 6.8 MB of documents, name frequency counting, co-occurrence network analysis, and drafting text.

**What the AI didn't do:** Decide which questions to ask. Design the four-level evidence framework. Identify that the prosecution memos in VOL00012 were the most important documents. Notice that Glen Dubin has never been publicly confronted despite being named in an SDNY memo with direct victim testimony. Recognize that "Cooperating Defendants: None" explains why no co-conspirators were ever indicted.

**What you can verify right now:** Every finding in this analysis cites specific EFTA document numbers. The documents are public. You can look them up. If the analysis says EFTA02731096 contains a victim's testimony about being directed to massage Glen Dubin, you can check whether EFTA02731096 says that. If it doesn't, the analysis is wrong. If it does, then the question of what tool was used to find it is irrelevant.

The entire EFTA release is ~7,700 pages of OCR text buried in 4,251 PDF files. Most media coverage has focused on names and headlines from press conferences. The prosecution memos — marked "Attorney Work Product" and "Subject to Fed. R. Crim. P. 6(e)" — are the most substantive documents in the release. They are also the ones almost nobody has read, because reading 18 files of OCR output is not something journalists on deadline do. It is something a person with a computer and two hours can do.

---

## What This Found

Findings from SDNY prosecution memoranda that have not appeared in mainstream media coverage:

- **Glen Dubin** — Maxwell explicitly instructed a victim to perform sexual acts on him. Named in SDNY memo EFTA02731113. Never investigated, never publicly confronted. This is the most actionable finding in the entire analysis.

- **Harvey Weinstein** — Epstein instructed a victim to massage Weinstein at the Paris residence. Weinstein ordered her to remove her shirt. She refused. Source: EFTA02731096. Not previously reported from primary EFTA documents.

- **Leon Black** — Subject of an active federal human trafficking referral in June 2023 (EFTA02731477), with an identified minor victim. This goes beyond the civil lawsuits that have been publicly reported.

- **"Cooperating Defendants: None"** — SDNY's memo (EFTA02731053) explicitly states they had zero cooperating defendants and planned to use Epstein's indictment as leverage. His death eliminated this strategy. This is the structural explanation for why no co-conspirators were indicted.

- **No cameras in bedrooms** — The memo explicitly states searches "did not reveal any cameras in any of the bedrooms or massage rooms." The blackmail narrative is not supported by the physical evidence found during the 2019 searches.

- **No client accounts** — "We have not identified any accounts that are consistent with Epstein handling or investing other people's money." The hedge fund manager myth is disproven in SDNY's own words.

- **Darren Indyke** (Epstein's attorney) told a witness not to talk to police and brought computers into prison for Epstein to have video sex. Source: EFTA02731123.

- **David Blaine** introduced a victim to Epstein at a NYC nightclub. Source: EFTA02731116.

- **Leslie Groff** was still actively recruiting in December 2018, six months before Epstein's arrest, and was never indicted despite being named throughout the prosecution memo.

---

## Documents

| File | Description |
|------|-------------|
| `analysis/epstein-v4-english.md` | Complete analysis (~2,400 words). All findings integrated with four evidence levels. |
| `analysis/epstein-findings-english.md` | Detailed findings report (~4,500 words). Full EFTA sourcing, redaction analysis, identity reconstruction. |
| `analysis/epstein-v4-norwegian.md` | Norwegian original of v4. |
| `analysis/epstein-findings-norwegian.md` | Norwegian original of the findings report. |

## Method

**Phase 1 — OCR:** 4,251 PDF files processed with Tesseract 4.1.1 (200 DPI, English). Output: ~6.8 MB cleaned text, 18 files.

**Phase 2 — Verification:** Each finding compared against 814 public sources.

**Phase 3 — Systematic analysis:** grep, Python (co-occurrence mapping, date extraction), manual reading. This phase located the prosecution memos in VOL00012.

**Tools:** Anthropic Claude for OCR processing, text search, and drafting. All analytical decisions were made by the author.

## How to Verify

1. Access the EFTA documents from the public release
2. Look up any EFTA number cited in the analysis
3. Read the document
4. Decide for yourself

If you find an error, open an issue. If you find something missed, open a pull request.

## Author

Adrian Moen. Fredrikstad, Norway. No journalistic or academic affiliation. Built this because the documents are public and someone should read them.

## License

Public domain.
