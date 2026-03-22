#!/usr/bin/env python3
"""Find correct EFTA numbers by extracting text from each PDF page directly."""

import pdfplumber
import re
import sys

PDF_PATH = "/Users/rentaladmin/Documents/Epstein Files Transparency Act (H.R.4405)/PDF-dokumenter/VOL00012/IMAGES/0001/EFTA02731082.pdf"
BASE_EFTA = 2731082

# Each entry: (label, search_patterns, old_efta_cited)
# search_patterns: list of (pattern, require_all=False)
# If require_all is a list, ALL patterns in the list must appear on same page
SEARCHES = [
    ("Glen Dubin / 'do to Glen'",
     [r"Glen and Eva Dubin", r"do to Glen"],
     "02731138"),

    ("Weinstein Paris massage",
     [r"massage Harvey Weinstein"],
     "02731096"),

    ("Cooperating Defendants",
     [r"Cooperating Defendants"],
     "02731053"),

    ("No cameras",
     [r"did not reveal any cameras"],
     "02731147"),

    ("Not handling other people's money",
     [r"handling or investing other people.s money"],
     None),

    ("Indyke 'don't talk to police'",
     [r"should not talk to the police"],
     "02731123"),

    ("Indyke bring computer to prison",
     [r"bring him a computer"],
     "02731126"),

    ("David Blaine nightclub",
     [r"David Bla[in]+e"],
     "02731116"),

    ("Leslie Groff emailed",
     [r"Leslie Groff emailed"],
     "02731126"),

    ("Jes Staley + raped",
     None,  # special: both must appear
     "02731113"),

    ("Wexner 'virtually all wealth'",
     [r"virtually all of Epstein.s wealth"],
     "02731146"),

    ("Leon Black massage/HT",
     [r"massage Leon Black"],
     "02731477"),

    ("Lent out so many times",
     [r"lent out so many times"],
     None),

    ("Prince Andrew + make him happy",
     None,  # special: both must appear
     None),
]

def main():
    print(f"Opening PDF: {PDF_PATH}")
    print(f"Base EFTA: {BASE_EFTA} (page 1)\n")

    # Extract text from every page
    pages = []
    with pdfplumber.open(PDF_PATH) as pdf:
        total = len(pdf.pages)
        print(f"Total pages: {total}\n")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append(text)
            if (i + 1) % 20 == 0:
                print(f"  Extracted {i+1}/{total} pages...")

    print(f"\nAll {total} pages extracted. Searching...\n")
    print("=" * 100)

    results = []

    for label, patterns, old_efta in SEARCHES:
        print(f"\n### {label}")
        print(f"    Old EFTA cited: {old_efta or '(none)'}")

        found_pages = []

        if label == "Jes Staley + raped":
            # Both "Jes Staley" and "raped" must appear on same page
            for pg_idx, text in enumerate(pages):
                if re.search(r"Jes Staley", text, re.IGNORECASE) and re.search(r"raped", text, re.IGNORECASE):
                    pg_num = pg_idx + 1
                    efta = BASE_EFTA + pg_idx
                    found_pages.append((pg_num, efta, text))
        elif label == "Prince Andrew + make him happy":
            for pg_idx, text in enumerate(pages):
                if re.search(r"Prince Andrew", text, re.IGNORECASE) and re.search(r"make him happy", text, re.IGNORECASE):
                    pg_num = pg_idx + 1
                    efta = BASE_EFTA + pg_idx
                    found_pages.append((pg_num, efta, text))
        else:
            for pg_idx, text in enumerate(pages):
                for pat in patterns:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        pg_num = pg_idx + 1
                        efta = BASE_EFTA + pg_idx
                        # Get snippet
                        start = max(0, m.start() - 50)
                        end = min(len(text), m.end() + 50)
                        snippet = text[start:end].replace('\n', ' ')
                        found_pages.append((pg_num, efta, snippet, pat))

        if not found_pages:
            print("    *** NOT FOUND ***")
            results.append((label, old_efta, "NOT FOUND", None))
        else:
            # Deduplicate by page
            seen = set()
            for entry in found_pages:
                pg_num, efta = entry[0], entry[1]
                if pg_num in seen:
                    continue
                seen.add(pg_num)
                new_efta = f"{efta:08d}"
                snippet = entry[2] if len(entry) > 2 else ""
                if len(entry) > 3:
                    print(f"    Page {pg_num} → EFTA{new_efta}  (matched: {entry[3]})")
                else:
                    print(f"    Page {pg_num} → EFTA{new_efta}")
                # Truncate snippet for display
                snip_display = snippet[:120].replace('\n', ' ') if isinstance(snippet, str) else ""
                if snip_display:
                    print(f"    Snippet: ...{snip_display}...")
                results.append((label, old_efta, new_efta, pg_num))

    # Correction table
    print("\n\n" + "=" * 100)
    print("CORRECTION TABLE")
    print("=" * 100)
    print(f"{'Claim':<40} {'OLD EFTA':<15} {'NEW EFTA':<15} {'Page':<6} {'Status'}")
    print("-" * 100)

    for label, old, new, page in results:
        if new == "NOT FOUND":
            status = "⚠️  NOT FOUND"
        elif old is None:
            status = "ℹ️  NEW (no old cite)"
        elif old == new:
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG — NEEDS FIX"

        print(f"{label:<40} {old or '—':<15} {new:<15} {str(page or '—'):<6} {status}")

if __name__ == "__main__":
    main()
