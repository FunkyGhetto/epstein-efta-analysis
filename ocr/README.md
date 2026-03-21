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

## Important: How to Read EFTA Numbers in These OCR Files

Each scanned PDF page has an EFTA number printed as a footer at the bottom of the page. When Tesseract processes the page, this footer is captured AFTER the page's body text in the OCR output. This means:

- The EFTA marker that appears BEFORE a passage in the OCR text belongs to the PREVIOUS page
- The EFTA marker that appears AFTER a passage is the correct page identifier for that passage
- In practice: if you grep for a passage and find EFTA02731138 as the nearest marker above it, the correct EFTA number for that passage is 02731139 (one higher)

This off-by-one pattern is consistent across all files. The analysis files in this repo cite the corrected (actual PDF page) EFTA numbers, not the OCR marker positions.

To verify any passage against the original PDF: find the EFTA marker BELOW the passage in the OCR file — that is the correct PDF page number.
