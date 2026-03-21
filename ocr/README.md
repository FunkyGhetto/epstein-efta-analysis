# OCR Source Files

These are the 18 cleaned OCR text files produced from 4,251 EFTA PDF documents using Tesseract 4.1.1 (200 DPI, English).

Total: ~6.8 MB across 18 files covering EFTA00000001 through EFTA02731789.

| Files | EFTA Range | Content |
|-------|-----------|---------|
| ren1-2 | 1–3848 | Photos, household docs, low text |
| ren3-10 | 3849–8294 | Depositions, phone records, CDRs |
| ren11-13 | 8295–9539 | Grand jury testimony, Acosta OPR interview |
| ren14-18 | 9540–2731789 | SDNY prosecution memos, FBI emails — most substantive |

To verify any finding in the analysis, grep for the EFTA number:

    grep -A 20 'EFTA02731114' epstein_ren16.txt

These files were OCR-processed by Adrian Moen. All analysis was performed by Claude (Anthropic).
