# Verification Tools

These tools were used to verify every EFTA citation in this repo against the original PDF documents. They require a local copy of the EFTA PDF release to function.

## EFTA Verifier (`verifier/app.py`)

A native macOS desktop app that renders original PDF pages alongside OCR text for side-by-side comparison. Used to confirm that every EFTA number cited in the analysis matches the correct page in the actual source document.

**What it does:**
- Takes an EFTA document number as input
- Finds the correct PDF across all 8 volumes (2,093 PDFs)
- Renders the page as an image and displays it next to the OCR text
- Supports searching multiple EFTA numbers at once
- Can export results as a ZIP with page images and text files

**Requirements:**
- macOS (uses Quartz for PDF rendering)
- Python 3 with: `pywebview`, `pypdf`
- A local copy of the EFTA PDF documents, organized as:
  ```
  ~/Documents/Epstein Files Transparency Act (H.R.4405)/
    PDF-dokumenter/
      VOL00001/IMAGES/0001/*.pdf
      VOL00002/IMAGES/0001/*.pdf
      ...
      VOL00012/IMAGES/0001/*.pdf
  ```

**To use with a different PDF location**, edit the `PDF_BASE` path near the top of `app.py`.

**Run:** `python3 tools/verifier/app.py`

## Citation Finder (`find_correct_efta.py`)

Extracts text from every page of a PDF independently (not from OCR files) and searches for key phrases. Used to discover and correct the off-by-one error in OCR-derived EFTA numbers.

## Final Verification (`final_verify.py`)

Checks every EFTA number cited in the repo against actual PDF text. The sign-off script that confirmed all 16 key citations are correct. Output: 16/16 verified, 0 failures.

## Why these tools are included

These tools are not meant to work out of the box. They are included in the repo to document the verification process. Every EFTA number in the analysis was checked against the original PDF pages using these scripts — not just trusted from OCR output.

If you download the EFTA PDFs yourself (they are public), you can run these tools to independently verify every finding.
