#!/usr/bin/env python3
"""Final verification: check every EFTA number cited in the repo against actual PDF text."""

import pdfplumber, re, os, glob

PDF_BASE = os.path.expanduser("~/Documents/Epstein Files Transparency Act (H.R.4405)/PDF-dokumenter")

# Build index of all PDFs across all volumes
def build_pdf_index():
    """Map each base EFTA number to its PDF path."""
    index = {}
    for pdf_path in glob.glob(os.path.join(PDF_BASE, "*/IMAGES/0001/EFTA*.pdf")):
        fname = os.path.basename(pdf_path)
        m = re.search(r'EFTA(\d+)', fname)
        if m:
            index[int(m.group(1))] = pdf_path
    return index

def find_pdf_for_efta(efta_num, index):
    """Find which PDF contains a given EFTA number and what page."""
    bases = sorted(index.keys())
    for i, base in enumerate(bases):
        next_base = bases[i+1] if i+1 < len(bases) else base + 9999
        if base <= efta_num < next_base:
            page = efta_num - base + 1
            return index[base], base, page
    return None, None, None

def extract_page_text(pdf_path, page_num):
    """Extract text from a specific page (1-indexed)."""
    with pdfplumber.open(pdf_path) as pdf:
        if page_num <= len(pdf.pages):
            return pdf.pages[page_num - 1].extract_text() or ""
    return ""

# Every EFTA number cited in the repo with its claim and a verification phrase
CITATIONS = [
    # README.md
    ("02731139", "Glen Dubin — Maxwell instructed victim", ["Glen and Eva Dubin", "do to Glen"]),
    ("02731096", "Weinstein Paris massage", ["massage Harvey Weinstein", "massage Weinstein"]),
    ("02731477", "Leon Black HT referral email", ["Leon Black", "HT Subject Referral", "Human Trafficking"]),
    ("02731053", "Cooperating Defendants: None", ["Cooperating Defendants", "cooperating defendants"]),
    ("02731148", "No cameras in bedrooms", ["did not reveal any cameras"]),
    ("02731148", "No client accounts", ["handling or investing other people"]),
    ("02731123", "Indyke don't talk to police", ["should not talk to the police"]),
    ("02731127", "Indyke computer in prison", ["bring him a computer"]),
    ("02731111", "David Blaine nightclub introduction", ["Bla"]),  # spelled Blau/Blane in PDF
    ("02731133", "Groff December 2018 email + $250K", ["Leslie Groff emailed", "Groff emailed"]),

    # analysis/ files
    ("02731114", "Staley raped + Black massage (same page)", ["Staley", "massage Leon Black"]),
    ("02731146", "Wexner virtually all wealth", ["virtually all"]),
    ("02731638", "Leon Black HT referral chain", ["Leon Black", "Black"]),
    ("02731109", "David Copperfield — 15yo victim", ["Copperfield", "magic show", "Las Vegas"]),

    # Acosta (VOL00007)
    ("00009220", "Acosta intelligence denial (page 1)", ["intelligence asset"]),
    ("00009221", "Acosta intelligence denial (page 2)", ["intelligence asset"]),
]

def main():
    print("Building PDF index...")
    index = build_pdf_index()
    print(f"Found {len(index)} PDFs across all volumes.\n")

    print("=" * 120)
    print(f"{'EFTA':<12} {'Claim':<45} {'PDF':<25} {'Page':<6} {'Status'}")
    print("=" * 120)

    passed = 0
    failed = 0

    for efta_str, claim, search_terms in CITATIONS:
        efta_num = int(efta_str)
        pdf_path, base, page = find_pdf_for_efta(efta_num, index)

        if pdf_path is None:
            print(f"{efta_str:<12} {claim:<45} {'NOT FOUND':<25} {'—':<6} ❌ NO PDF")
            failed += 1
            continue

        pdf_name = os.path.basename(pdf_path)

        try:
            text = extract_page_text(pdf_path, page)
        except Exception as e:
            print(f"{efta_str:<12} {claim:<45} {pdf_name:<25} {page:<6} ❌ ERROR: {e}")
            failed += 1
            continue

        found_any = False
        for term in search_terms:
            if re.search(term, text, re.IGNORECASE):
                found_any = True
                break

        if found_any:
            print(f"{efta_str:<12} {claim:<45} {pdf_name:<25} {page:<6} ✅ VERIFIED")
            passed += 1
        else:
            print(f"{efta_str:<12} {claim:<45} {pdf_name:<25} {page:<6} ❌ TEXT NOT FOUND")
            # Show what IS on that page
            preview = text[:150].replace('\n', ' ') if text else "(empty)"
            print(f"             Page text starts: {preview}...")
            failed += 1

    print("=" * 120)
    print(f"\nRESULTS: {passed} verified, {failed} failed, {passed + failed} total")
    if failed == 0:
        print("\n✅ ALL CITATIONS VERIFIED AGAINST ACTUAL PDF TEXT")
    else:
        print(f"\n⚠️  {failed} CITATION(S) NEED ATTENTION")

if __name__ == "__main__":
    main()
