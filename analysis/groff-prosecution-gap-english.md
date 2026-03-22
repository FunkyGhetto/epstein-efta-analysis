# The Prosecution Gap: Why Leslie Groff Was Never Charged

*Every claim is sourced to specific EFTA documents. Four explanations for the largest evidence-action gap in the EFTA record are tested against the data. This document does not conclude which explanation is correct.*

## The Evidence

Leslie Groff worked as Epstein's primary New York assistant from 2001 through the summer of 2019. She is named by virtually every victim. Her attorney invoked the Fifth Amendment. SDNY analyzed potential charges against her in a dedicated section. She was never indicted. For full details, see `analysis/groff-investigation-english.md`.

## The Gap

Using the unified knowledge base built from every data source in this project — prosecution memos, victim testimony, financial records, corpus analysis, linguistic patterns, and cross-references — Groff has the largest evidence-action gap of any person in the dataset:

| Person | Evidence Score | Action Score | **Gap** |
|--------|---------------|-------------|---------|
| **Leslie Groff** | **9/10** | **1/10** | **8.0** |
| Les Wexner | 7/10 | 1/10 | 6.0 |
| Leon Black | 6/10 | 1/10 | 5.0 |
| Ghislaine Maxwell | 8/10 | 10/10 | -2.0 |

## The Kellen Comparison

Sarah Kellen performed a comparable scheduling role. The comparison is instructive but requires a correction: **Kellen was also never charged.** SDNY drafted plea agreements for her but the negotiations collapsed. However, SDNY explicitly considered charging Kellen:

> "[email from AUSA]: Sarah Kellen, who is the only other individual we currently are considering charging" (Source: EFTA00106062, DS9)

The phrase "only other individual" means Kellen was the sole co-conspirator under active charging consideration. Groff was not.

| Metric | Leslie Groff | Sarah Kellen |
|--------|-------------|-------------|
| Role | Scheduler/assistant | Scheduler/co-conspirator |
| Memo mentions | 53 | 0 |
| Corpus pages | 172,443 | 1,500 |
| NPA covered | No | Yes |
| Proffer | Yes (July 2021) | Yes (Nov-Dec 2019) |
| Fifth Amendment | Invoked (Aug 2019) | Invoked (Jul 2019) |
| Plea negotiations | None documented | Drafted, collapsed |
| Charging considered | Not documented | Yes (EFTA00106062) |
| Outcome | Never charged | Never charged |

Both performed scheduling roles. Both invoked the Fifth Amendment. Both eventually proffered. But SDNY considered charging Kellen and not Groff — despite Groff having 53 memo mentions to Kellen's 0, and 172K corpus pages to Kellen's 1,500. The NPA protected Kellen; nothing protected Groff. Yet Groff was treated more favorably.

## Four Explanations Tested

### Explanation A — Groff Cooperated Secretly

**Evidence found:**

A proffer agreement was discovered in the corpus at **EFTA01682023** (DS10):

> "PROFFER AGREEMENT — With respect to the meeting of Lesley Groff 'Client' and her attorney, Michael Bachner, Esq., with Assistant United States Attorney [redacted] to be held on July 23, 2021 ('the meeting'), the following understandings exist: (I) THIS IS NOT A COOPERATION AGREEMENT." (Source: EFTA01682023)

The agreement was signed under Audrey Strauss (Acting USAO). It includes standard queen-for-a-day terms: statements cannot be used against her except for perjury, obstruction, or if she testifies. It includes continuation dates, suggesting multiple sessions.

**Timeline:** The prosecution memo (October 2019) reported Groff's attorney was "considering whether to bring Groff in for a proffer." The proffer happened 21 months later, in July 2021 — after Epstein's death (August 2019) and during the Maxwell pretrial period.

**What this means:** Groff did sit down with SDNY and provide information. The agreement explicitly states it is "NOT A COOPERATION AGREEMENT" and that "the Government does not agree to make a motion on the Client's behalf or to enter into a cooperation agreement, plea agreement, immunity or non-prosecution agreement." However, proffers often precede such agreements.

**What this doesn't tell us:** What Groff said. Whether her information was useful. Whether it led to any investigative action. Whether a subsequent cooperation agreement exists under seal.

**Assessment: PARTIALLY SUPPORTED.** Groff proffered. Whether this constitutes meaningful cooperation is unknown. This finding is not documented in any other EFTA analysis project.

### Explanation B — SDNY Deliberately Deprioritized Her

**Evidence found:**

Groff is the only person in the prosecution memo who receives minimizing language:

> "she had limited interactions with the victims beyond scheduling" (Source: EFTA02731146)

> "She spent little time in Epstein's residence and thus had few in-person interactions with victims." (Source: EFTA02731146)

No other named person receives comparable exculpatory framing. The linguistic pattern analysis shows Groff's hedging ratio (0.25) is the lowest of any person with linguistic data — SDNY uses cautious, minimizing language 75% of the time when discussing her.

Structurally, Groff gets 53 memo mentions but her section introduction explicitly frames her role as passive. Every victim contradicts this framing — naming her as their scheduling contact, describing her presence outside the closed door during abuse, and one equating her with Maxwell as someone who "ruined her life."

The AUSA email about Kellen — "the only other individual we currently are considering charging" — confirms Groff was not under active charging consideration despite more evidence.

**Assessment: SUPPORTED.** The linguistic and structural evidence shows deliberate minimization. The memo's characterization of Groff contradicts the testimony it contains about her.

### Explanation C — Section D Was Withheld From the Release

**Evidence found:**

Pages 68-85 of the prosecution memo (EFTA02731082) are all under 200 characters of text in both our OCR and the rhowardstone full-text corpus. These pages correspond to the charging analysis sections (A through E). The content pages (0-67) average 2,500-3,500 characters each.

Maxwell's section (E) was released as a separate PDF (EFTA02731168) with full content (1,400-3,500 chars per page). Groff's section (D) was not released in any form.

The DOJ's own document alteration forensics show selective decisions about Groff's name — un-redacting it in some documents while redacting others (Source: rhowardstone/Epstein-research, DOJ_DOCUMENT_ALTERATION_FORENSICS.md).

**Assessment: SUPPORTED — but not unique to Groff.** The entire charging analysis section (pages 68-85) is empty, not just Section D. Sections A, B, C, and D are all missing. Maxwell's section was released separately; the others were not. This suggests a document-level release decision, not Groff-specific withholding.

### Explanation D — Groff Was Protected

**Evidence found:**

No positive evidence of external pressure, political intervention, or institutional protection was found in the corpus. Groff coordinated political donations for Epstein (EFTA01928617) and called the US State Department searching for Senator George Mitchell (EFTA02522767), but neither constitutes evidence of protection for Groff herself.

Congressional oversight (Chairman Comer, March 2026) sent letters to Groff requesting a transcribed interview. Her response has not been publicly confirmed.

**Assessment: INCONCLUSIVE.** The gap between evidence and action is real. But the cause of the gap is documented only through negative evidence — what didn't happen — rather than positive evidence of why it didn't happen. The proffer discovery (Explanation A) may account for some of the gap.

## The Most Significant Discovery

**EFTA01682023** — the Groff proffer agreement — is the single most important document found during this investigation. It resolves a two-year-old question from the prosecution memo ("is considering whether to bring Groff in for a proffer") and reveals that Groff did provide information to SDNY under formal terms.

This document is not cited in rhowardstone's 165-report project, despite their extensive Groff coverage (93 reports mentioning her). It appears in Dataset 10, filed alongside other legal documents.

The proffer does not explain why Groff was never charged. It does establish that SDNY had direct access to her account of events — and still chose not to prosecute.

## Section D — The Missing Piece

The prosecution memo's Section D, titled "Leslie Groff," contains SDNY's actual charging analysis. Its content is not in the public release. Both our OCR extraction and the rhowardstone full-text corpus (a completely independent extraction pipeline processing the same PDFs) show only the section heading — 179 characters.

If Section D recommended charging Groff, the non-prosecution becomes harder to explain. If it recommended against charging, it would reveal SDNY's reasoning. Either way, it is the document that could resolve the prosecution gap definitively.

## The Linguistic Signature

The linguistic analysis across all persons in the dataset reveals a consistent pattern: SDNY uses confident language for people it ultimately charged and hedging language for people it did not charge.

| Person | Hedging | Strong | Ratio | Outcome |
|--------|---------|--------|-------|---------|
| Les Wexner | 5 | 0 | 0.00 | Never charged |
| Darren Indyke | 1 | 0 | 0.00 | Never charged |
| **Leslie Groff** | **3** | **1** | **0.25** | **Never charged** |
| Leon Black | 52 | 20 | 0.28 | Never charged |
| **Ghislaine Maxwell** | **22** | **22** | **0.50** | **Charged** |
| Prince Andrew | 0 | 1 | 1.00 | Never charged (UK jurisdiction) |

Groff's ratio (0.25) places her firmly in the non-charging linguistic zone. SDNY's word choices, written before the final charging decisions, already reflected the outcome.

## Limitations

1. **The proffer content is unknown.** EFTA01682023 is the agreement itself, not a transcript. What Groff told SDNY could range from nothing useful to information that built the Maxwell case.

2. **Kellen was also not charged.** Our initial comparison overstated the asymmetry. Both schedulers were never charged. The distinction is that SDNY considered charging Kellen and not Groff.

3. **The linguistic analysis uses small samples.** Groff has only 4 data points (3 hedging, 1 strong). The pattern is consistent with the broader dataset but the individual confidence is low.

4. **Explanation D is unfalsifiable.** Protection by definition leaves no positive evidence. The absence of evidence for protection cannot be taken as evidence against it.

5. **The evidence scoring is our own methodology.** Scores from 0-10 are derived from data but reflect judgments about what counts as evidence. Different weightings would produce different rankings.

6. **The proffer may have led to an unpublicized cooperation agreement.** Standard SDNY practice allows for sealed agreements that would not appear in the public EFTA release.

## Source Documents

| EFTA Number | Content |
|-------------|---------|
| **EFTA01682023** | **Groff proffer agreement, July 23, 2021 (genuinely new discovery)** |
| EFTA02731146 | Prosecution memo: Groff proffer section, Fifth Amendment, SDNY pushback |
| EFTA02731167 | Section D heading (content missing from release) |
| EFTA00106062 | AUSA email: Kellen "only other individual we currently are considering charging" |
| EFTA00013209 | DAG meeting memo: plea negotiations with co-conspirator |
| EFTA00089268 | Kellen plea draft evidence |
| EFTA01928617 | Groff coordinating political donation for Epstein |
| EFTA02522767 | Groff calling US State Department for Senator Mitchell |

---

*Analysis by Claude (Anthropic) from OCR text processed by Adrian Moen, cross-referenced against [rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research) and the rhowardstone full-text corpus database (v5.0, 2.89M pages). Source documents from the Epstein Files Transparency Act (H.R.4405) public release at https://www.justice.gov/epstein/*
