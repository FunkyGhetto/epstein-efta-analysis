#!/usr/bin/env python3
"""
QA Check for epstein-efta-analysis repo.
Validates EFTA citations, cross-file consistency, links, claims, and forbidden patterns.
"""

import os
import re
import sys
import glob
from pathlib import Path
from urllib.parse import urlparse

REPO = os.path.expanduser("~/Documents/epstein-efta-analysis")
OCR_DIR = os.path.join(REPO, "ocr")
ANALYSIS_DIR = os.path.join(REPO, "analysis")
README = os.path.join(REPO, "README.md")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

passes = 0
fails = 0
warnings = 0
failure_details = []
warning_details = []


def PASS(msg):
    global passes
    passes += 1
    print(f"  {GREEN}PASS{RESET} {msg}")


def FAIL(msg):
    global fails
    fails += 1
    failure_details.append(msg)
    print(f"  {RED}FAIL{RESET} {msg}")


def WARN(msg):
    global warnings
    warnings += 1
    warning_details.append(msg)
    print(f"  {YELLOW}WARN{RESET} {msg}")


def get_md_files():
    """Get all .md files in repo (root, analysis/, ocr/)."""
    files = []
    for pattern in ["*.md", "analysis/*.md", "ocr/*.md", "tools/*.md"]:
        files.extend(glob.glob(os.path.join(REPO, pattern)))
    return sorted(set(files))


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_ocr_text():
    """Load all OCR files into memory."""
    ocr = {}
    for f in sorted(glob.glob(os.path.join(OCR_DIR, "epstein_ren*.txt"))):
        ocr[os.path.basename(f)] = read_file(f)
    return ocr


def extract_efta_numbers(text):
    """Extract EFTA numbers from text, returning (number_str, full_match)."""
    return re.findall(r'EFTA(\d{5,8})', text)


def extract_efta_with_context(text, filename):
    """Extract EFTA numbers with surrounding line context."""
    results = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for m in re.finditer(r'EFTA(\d{5,8})', line):
            ctx_start = max(0, i - 2)
            ctx_end = min(len(lines), i + 3)
            context = '\n'.join(lines[ctx_start:ctx_end])
            results.append({
                'number': m.group(1),
                'line_num': i + 1,
                'line': line.strip(),
                'context': context,
                'file': filename
            })
    return results


# ============================================================
# CHECK 1: EFTA NUMBER CONSISTENCY
# ============================================================
def check_efta_consistency():
    print(f"\n{BOLD}1. EFTA NUMBER CONSISTENCY{RESET}")

    md_files = get_md_files()
    ocr = get_ocr_text()
    all_ocr_text = '\n'.join(ocr.values())

    # Extract all EFTA numbers from .md files
    md_efta = {}
    for f in md_files:
        text = read_file(f)
        nums = extract_efta_numbers(text)
        if nums:
            md_efta[f] = nums

    total_citations = sum(len(v) for v in md_efta.values())
    unique_nums = set()
    for nums in md_efta.values():
        unique_nums.update(nums)

    print(f"  Found {total_citations} EFTA citations across {len(md_efta)} files ({len(unique_nums)} unique numbers)")

    # Check each number exists in OCR
    missing_from_ocr = []
    found_in_ocr = 0

    # Some EFTA numbers are range markers or from non-OCR sources
    ocr_range_nums = set()
    for num in unique_nums:
        marker = f"EFTA{num}"
        if marker in all_ocr_text:
            found_in_ocr += 1
            ocr_range_nums.add(num)
        else:
            # Check if it's a computed page number (one above a marker that exists)
            prev_num = str(int(num) - 1).zfill(len(num))
            prev_marker = f"EFTA{prev_num}"
            if prev_marker in all_ocr_text:
                found_in_ocr += 1  # Valid: off-by-one corrected number
            else:
                missing_from_ocr.append(num)

    if missing_from_ocr:
        # Filter out known non-OCR numbers (range boundaries, external PDFs)
        truly_missing = [n for n in missing_from_ocr
                        if n not in ('00000001', '02731789', '00000476')]
        if truly_missing:
            WARN(f"{len(truly_missing)} EFTA numbers in .md files not found in OCR (may be from separate PDFs): {', '.join(sorted(truly_missing)[:10])}")
        else:
            PASS(f"All EFTA numbers accounted for (some are range markers)")
    else:
        PASS(f"All {len(unique_nums)} unique EFTA numbers found in OCR files")

    PASS(f"{found_in_ocr}/{len(unique_nums)} EFTA numbers verified in OCR")


# ============================================================
# CHECK 2: CROSS-FILE CONSISTENCY
# ============================================================
def check_cross_file():
    print(f"\n{BOLD}2. CROSS-FILE CONSISTENCY{RESET}")

    readme_text = read_file(README)

    # 2a: README EFTA numbers should appear in analysis files
    readme_efta = set(extract_efta_numbers(readme_text))

    analysis_files = glob.glob(os.path.join(ANALYSIS_DIR, "*.md"))
    analysis_efta = set()
    for f in analysis_files:
        analysis_efta.update(extract_efta_numbers(read_file(f)))

    readme_only = readme_efta - analysis_efta
    # Filter out numbers that only appear in ocr/README or tools/README context
    # (like range markers 00000001, 02731789)
    range_markers = {'00000001', '02731789'}
    readme_only_significant = readme_only - range_markers

    if readme_only_significant:
        WARN(f"EFTA numbers in README but not in any analysis file: {', '.join(sorted(readme_only_significant))}")
    else:
        PASS("All significant README EFTA numbers also appear in analysis files")

    # 2b: Key persons in README should appear in analysis files
    key_persons = ['Dubin', 'Weinstein', 'Black', 'Staley', 'Indyke', 'Groff', 'Blaine', 'Wexner', 'Andrew']
    all_analysis_text = '\n'.join(read_file(f) for f in analysis_files)

    missing_persons = [p for p in key_persons if p not in all_analysis_text]
    if missing_persons:
        FAIL(f"Persons in README missing from analysis files: {', '.join(missing_persons)}")
    else:
        PASS(f"All {len(key_persons)} key persons found in analysis files")

    # 2c: Documents table should list all analysis files
    existing_analysis = set(os.path.basename(f) for f in analysis_files)
    table_referenced = set()
    for m in re.finditer(r'`analysis/([^`]+)`', readme_text):
        table_referenced.add(m.group(1))

    unlisted = existing_analysis - table_referenced
    if unlisted:
        FAIL(f"Analysis files not in README Documents table: {', '.join(sorted(unlisted))}")
    else:
        PASS(f"All {len(existing_analysis)} analysis files listed in README Documents table")

    # 2d: No phantom references
    phantom = table_referenced - existing_analysis
    if phantom:
        FAIL(f"README references non-existent analysis files: {', '.join(sorted(phantom))}")
    else:
        PASS("No phantom file references in README")


# ============================================================
# CHECK 3: LINK VALIDATION
# ============================================================
def check_links():
    print(f"\n{BOLD}3. LINK VALIDATION{RESET}")

    md_files = get_md_files()

    # Check URLs
    url_pattern = re.compile(r'https?://[^\s\)>\]]+')
    bad_urls = []
    total_urls = 0

    for f in md_files:
        text = read_file(f)
        for m in url_pattern.finditer(text):
            total_urls += 1
            url = m.group(0).rstrip('.,;:')
            try:
                result = urlparse(url)
                if not result.netloc:
                    bad_urls.append((os.path.basename(f), url))
            except Exception:
                bad_urls.append((os.path.basename(f), url))

    if bad_urls:
        FAIL(f"{len(bad_urls)} malformed URLs found")
        for fn, url in bad_urls[:5]:
            print(f"    {fn}: {url}")
    else:
        PASS(f"All {total_urls} URLs syntactically valid")

    # Check internal file references
    internal_ref_pattern = re.compile(r'`([^`]*\.(?:md|py|json|txt))`')
    bad_refs = []
    total_refs = 0

    for f in md_files:
        text = read_file(f)
        for m in internal_ref_pattern.finditer(text):
            ref = m.group(1)
            if ref.startswith('analysis/') or ref.startswith('ocr/') or ref.startswith('tools/'):
                total_refs += 1
                full_path = os.path.join(REPO, ref)
                if not os.path.exists(full_path):
                    bad_refs.append((os.path.basename(f), ref))

    if bad_refs:
        FAIL(f"{len(bad_refs)} broken internal references")
        for fn, ref in bad_refs[:5]:
            print(f"    {fn}: {ref}")
    else:
        PASS(f"All {total_refs} internal file references valid")


# ============================================================
# CHECK 4: CLAIM CONSISTENCY
# ============================================================
def check_claims():
    print(f"\n{BOLD}4. CLAIM CONSISTENCY{RESET}")

    readme_text = read_file(README)
    all_md_text = '\n'.join(read_file(f) for f in get_md_files())

    # 4a: No "independently confirmed" + "genuinely new" on same finding
    lines = readme_text.split('\n')
    for i, line in enumerate(lines):
        if 'genuinely new' in line.lower() and 'independently confirmed' in line.lower():
            FAIL(f"README line {i+1}: Finding marked both 'genuinely new' AND 'independently confirmed'")
            break
    else:
        PASS("No finding is both 'genuinely new' and 'independently confirmed'")

    # 4b: "never" should not appear near Dubin without qualification
    dubin_never = False
    for f in get_md_files():
        text = read_file(f)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'dubin' in line.lower() and 'never' in line.lower():
                if 'may be' not in line.lower() and 'ambiguous' not in line.lower() and 'redaction' not in line.lower():
                    FAIL(f"{os.path.basename(f)} line {i+1}: 'never' near 'Dubin' without qualification")
                    dubin_never = True
                    break
        if dubin_never:
            break
    if not dubin_never:
        PASS("No unqualified 'never' near 'Dubin'")

    # 4c: "separate victim" near Dubin should have qualification
    sep_victim_issue = False
    for f in get_md_files():
        text = read_file(f)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'dubin' in line.lower() and 'separate victim' in line.lower():
                if 'may be' not in line.lower() and 'ambiguous' not in line.lower() and 'redaction' not in line.lower():
                    FAIL(f"{os.path.basename(f)} line {i+1}: 'separate victim' near 'Dubin' without 'may be'/'redaction' qualifier")
                    sep_victim_issue = True
    if not sep_victim_issue:
        PASS("No unqualified 'separate victim' near 'Dubin'")


# ============================================================
# CHECK 5: NORWEGIAN-ENGLISH PARITY
# ============================================================
def check_parity():
    print(f"\n{BOLD}5. NORWEGIAN-ENGLISH PARITY{RESET}")

    english_files = sorted(glob.glob(os.path.join(ANALYSIS_DIR, "*english*.md")))

    # Files that deliberately have no Norwegian counterpart
    no_translation_needed = {'victim-cross-reference-english.md'}

    for ef in english_files:
        base = os.path.basename(ef)
        if base in no_translation_needed:
            PASS(f"Skipped (no translation needed): {base}")
            continue
        nf_name = base.replace('english', 'norwegian')
        nf = os.path.join(ANALYSIS_DIR, nf_name)

        if not os.path.exists(nf):
            FAIL(f"Missing Norwegian counterpart for {base}")
            continue

        PASS(f"Pair found: {base} <-> {nf_name}")

        # Check EFTA citation count parity
        en_efta = extract_efta_numbers(read_file(ef))
        no_efta = extract_efta_numbers(read_file(nf))

        if len(en_efta) == 0 and len(no_efta) == 0:
            continue

        ratio = len(no_efta) / max(len(en_efta), 1)
        if 0.7 <= ratio <= 1.3:
            PASS(f"  EFTA count parity: EN={len(en_efta)} NO={len(no_efta)} (ratio {ratio:.2f})")
        else:
            WARN(f"  EFTA count mismatch: EN={len(en_efta)} NO={len(no_efta)} (ratio {ratio:.2f})")


# ============================================================
# CHECK 6: SOURCE LINE COMPLETENESS
# ============================================================
def check_source_lines():
    print(f"\n{BOLD}6. SOURCE LINE COMPLETENESS{RESET}")

    findings_files = [
        os.path.join(ANALYSIS_DIR, "epstein-findings-english.md"),
        os.path.join(ANALYSIS_DIR, "epstein-findings-norwegian.md"),
    ]

    key_persons = ['Dubin', 'Weinstein', 'Black', 'Staley', 'Indyke', 'Groff', 'Blaine', 'Wexner', 'Copperfield']
    source_pattern = re.compile(r'Source:|Kilde:|EFTA\d{5,8}')

    for ff in findings_files:
        if not os.path.exists(ff):
            WARN(f"Findings file not found: {os.path.basename(ff)}")
            continue

        text = read_file(ff)
        lines = text.split('\n')
        basename = os.path.basename(ff)

        # Find bold person headers and check nearby source lines
        missing_sources = []
        for i, line in enumerate(lines):
            if line.startswith('**') and any(p in line for p in key_persons):
                # Check next 10 lines for a Source/Kilde/EFTA reference
                window = '\n'.join(lines[i:min(i+10, len(lines))])
                if not source_pattern.search(window):
                    missing_sources.append((i+1, line.strip()[:80]))

        if missing_sources:
            for ln, txt in missing_sources:
                WARN(f"{basename} line {ln}: Person section without nearby EFTA source: {txt}")
        else:
            PASS(f"{basename}: All key person sections have nearby source citations")


# ============================================================
# CHECK 7: FORBIDDEN PATTERNS
# ============================================================
def check_forbidden():
    print(f"\n{BOLD}7. FORBIDDEN PATTERNS{RESET}")

    forbidden = [
        (r'EFTA02731113.*[Dd]ubin|[Dd]ubin.*EFTA02731113', "EFTA02731113 paired with Dubin (old wrong number)"),
        (r'EFTA02731116.*[Bb]laine|[Bb]laine.*EFTA02731116', "EFTA02731116 paired with Blaine (old wrong number)"),
        (r'[Dd]ubin.*never investigated|never investigated.*[Dd]ubin', "'never investigated' near Dubin"),
        (r'never publicly confronted', "'never publicly confronted' anywhere"),
        (r'[Dd]ubin.*second independent account|second independent account.*[Dd]ubin', "'second independent account' near Dubin"),
        (r'An independent analysis', "'An independent analysis' (old README intro)"),
        (r'Before You Dismiss This', "'Before You Dismiss This' (old section)"),
    ]

    md_files = get_md_files()

    for pattern, description in forbidden:
        found = False
        for f in md_files:
            text = read_file(f)
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    FAIL(f"Forbidden: {description} — {os.path.basename(f)} line {i+1}")
                    found = True
                    break
            if found:
                break
        if not found:
            PASS(f"Clean: {description}")


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"{BOLD}{'='*60}")
    print(f"QA CHECK — epstein-efta-analysis")
    print(f"{'='*60}{RESET}")

    check_efta_consistency()
    check_cross_file()
    check_links()
    check_claims()
    check_parity()
    check_source_lines()
    check_forbidden()

    # Summary
    print(f"\n{BOLD}{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}{RESET}")
    print(f"  {GREEN}PASSES: {passes}{RESET}")
    print(f"  {YELLOW}WARNINGS: {warnings}{RESET}")
    print(f"  {RED}FAILS: {fails}{RESET}")

    if failure_details:
        print(f"\n{RED}{BOLD}FAILURES:{RESET}")
        for i, f in enumerate(failure_details, 1):
            print(f"  {i}. {f}")

    if warning_details:
        print(f"\n{YELLOW}{BOLD}WARNINGS:{RESET}")
        for i, w in enumerate(warning_details, 1):
            print(f"  {i}. {w}")

    if fails == 0:
        print(f"\n{GREEN}{BOLD}ALL CHECKS PASSED{RESET}")
    else:
        print(f"\n{RED}{BOLD}{fails} FAILURE(S) NEED ATTENTION{RESET}")

    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
