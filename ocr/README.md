# OCR Source Files

18 cleaned OCR text files produced from 4,251 EFTA PDF documents using Tesseract 4.1.1 (200 DPI, English). OCR processing by Adrian Moen. All analysis performed by Claude (Anthropic).

Total: ~6.8 MB covering EFTA00000001 through EFTA02731789.

| Files | EFTA Range | Content |
|-------|-----------|---------|
| ren1-2 | 1–3848 | Photos, household docs, low text |
| ren3-10 | 3849–8294 | Depositions, phone records, CDRs |
| ren11-13 | 8295–9539 | Grand jury testimony, Acosta OPR interview |
| ren14-18 | 9540–2731789 | SDNY prosecution memos, FBI emails — most substantive |

## How EFTA Page Numbers Work in These Files

Each scanned PDF page has an EFTA number printed as a footer. When Tesseract processes a page, this footer is captured AFTER the page's body text. This means:

- The EFTA marker that appears BEFORE a passage belongs to the PREVIOUS page
- The EFTA marker that appears AFTER a passage is the correct page number for that passage
- Example: text between EFTA02731138 and EFTA02731139 belongs to page EFTA02731139

The analysis files in this repo cite the corrected (actual PDF page) EFTA numbers, verified by extracting text from every page of the original PDFs independently.

## How to Verify a Finding

To find the OCR text for a specific EFTA page, grep for the marker one number BELOW the cited page:

    grep -A 20 'EFTA02731113' epstein_ren16.txt

This shows the content of page EFTA02731114 (Staley/Black massage passage). The text appears after the 02731113 marker and before the 02731114 marker — because the 02731113 marker is the footer of the previous page.
