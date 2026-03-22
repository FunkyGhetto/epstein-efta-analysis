# OCR Source Files

These are the 18 cleaned OCR text files produced from 4,251 EFTA PDF documents using Tesseract 4.1.1 (200 DPI, English).

Total: ~6.8 MB across 18 files covering EFTA00000001 through EFTA02731789.

| Files | EFTA Range | Content |
|-------|-----------|---------|
| ren1-2 | 1–3848 | Photos, household docs, low text |
| ren3-10 | 3849–8294 | Depositions, phone records, CDRs |
| ren11-13 | 8295–9539 | Grand jury testimony, Acosta OPR interview |
| ren14-18 | 9540–2731789 | SDNY prosecution memos, FBI emails — most substantive |

To verify any finding, grep for the EFTA marker one number BELOW the cited page (see explanation below):

    grep -A 20 'EFTA02731113' epstein_ren16.txt

This shows the content of page EFTA02731114 (Staley/Black massage passage).

These files were OCR-processed by Adrian Moen. All analysis was performed by Claude (Anthropic).

## How EFTA Numbers Work in These OCR Files

Each scanned PDF page has an EFTA number printed as a footer at the bottom. When Tesseract processes the page, this footer is captured AFTER the page's body text. This means:

- The EFTA marker that appears BEFORE a passage in the OCR text belongs to the PREVIOUS page
- The EFTA marker that appears AFTER a passage is the correct page number for that passage
- Example: if you find text with EFTA02731138 above it and EFTA02731139 below it, the text belongs to page EFTA02731139

The analysis files in this repo cite the corrected (actual PDF page) EFTA numbers, verified by extracting text from every page of the original PDFs independently.

To verify: find the EFTA marker BELOW your passage in the OCR file — that is the correct PDF page number.
