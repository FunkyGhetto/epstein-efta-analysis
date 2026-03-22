#!/usr/bin/env python3
"""
Verify EFTA findings by extracting the exact page from the source PDF.

Usage: python3 verify.py 02731113
"""

import sys
import os
import subprocess
import tempfile
from pypdf import PdfReader, PdfWriter

PDF_DIR = os.path.expanduser(
    "~/Documents/Epstein Files Transparency Act (H.R.4405)/"
    "PDF-dokumenter/VOL00012/IMAGES/0001/"
)


def get_pdf_index(pdf_dir):
    """Build sorted list of (efta_number, filename) for all PDFs."""
    entries = []
    for f in os.listdir(pdf_dir):
        if f.startswith("EFTA") and f.endswith(".pdf"):
            num = int(f.replace("EFTA", "").replace(".pdf", ""))
            entries.append((num, f))
    return sorted(entries)


def find_pdf(target, index):
    """Find which PDF contains the target EFTA number."""
    match = None
    for efta_num, filename in index:
        if efta_num <= target:
            match = (efta_num, filename)
        else:
            break
    if match is None:
        return None, None, None

    efta_num, filename = match
    page = target - efta_num  # 0-indexed
    reader = PdfReader(os.path.join(PDF_DIR, filename))
    if page < 0 or page >= len(reader.pages):
        return None, None, None
    return filename, page, len(reader.pages)


def extract_and_open(filename, page_index, target):
    """Extract a single page to a temp PDF and open in Preview."""
    src_path = os.path.join(PDF_DIR, filename)
    reader = PdfReader(src_path)
    writer = PdfWriter()
    writer.add_page(reader.pages[page_index])

    tmp = os.path.join(tempfile.gettempdir(), f"EFTA{target:08d}.pdf")
    with open(tmp, "wb") as f:
        writer.write(f)

    subprocess.run(["open", "-a", "Preview", tmp])
    return tmp


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify.py <EFTA-number>")
        print("Example: python3 verify.py 02731113")
        sys.exit(1)

    if not os.path.isdir(PDF_DIR):
        print(f"ERROR: PDF directory not found: {PDF_DIR}")
        sys.exit(1)

    # Handle single lookup or --test mode
    if sys.argv[1] == "--test":
        run_test()
        return

    target = int(sys.argv[1])
    index = get_pdf_index(PDF_DIR)
    filename, page_index, total_pages = find_pdf(target, index)

    if filename is None:
        print(f"ERROR: EFTA{target:08d} not found in any PDF.")
        sys.exit(1)

    page_human = page_index + 1  # 1-indexed for display
    print(f"EFTA{target:08d}")
    print(f"  PDF:  {filename}")
    print(f"  Page: {page_human} of {total_pages}")
    print(f"  Opening in Preview...")

    tmp = extract_and_open(filename, page_index, target)
    print(f"  Saved: {tmp}")


def run_test():
    """Test all key EFTA numbers from the analysis."""
    test_cases = [
        (2731113, "Dubin + Staley testimony"),
        (2731096, "Weinstein Paris massage"),
        (2731477, "Leon Black HT referral email"),
        (2731053, "Cooperating Defendants: None"),
        (2731147, "No cameras + no client accounts"),
        (2731123, "Indyke 'don't talk to police'"),
        (2731126, "Indyke computer in prison + Groff Dec 2018 + $250K wire"),
        (2731116, "David Blaine nightclub introduction"),
        (2731146, "Wexner 'virtually all of Epstein's wealth'"),
        (2731638, "Leon Black HT referral - second email in chain"),
    ]

    index = get_pdf_index(PDF_DIR)

    print("=" * 80)
    print(f"{'EFTA Number':<16} {'PDF File':<24} {'Page':>8}  Claim")
    print("-" * 80)

    all_ok = True
    for target, claim in test_cases:
        filename, page_index, total_pages = find_pdf(target, index)
        if filename is None:
            print(f"EFTA{target:08d}    NOT FOUND                        {claim}")
            all_ok = False
        else:
            page_human = page_index + 1
            print(
                f"EFTA{target:08d}  {filename:<24} {page_human:>4}/{total_pages:<4} {claim}"
            )

    print("=" * 80)
    if all_ok:
        print("All 10 EFTA numbers resolved successfully.")
    else:
        print("WARNING: Some EFTA numbers could not be resolved.")


if __name__ == "__main__":
    main()
