#!/usr/bin/env python3
"""
Phone pattern analysis: extract phone numbers from CDR files (ren3-ren10).
Identify frequently called numbers, cross-location numbers, and call clusters.

Output: phone_patterns.json, phone_patterns.txt
"""

import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime

OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# CDR files are primarily ren3-ren10, but scan ren2-ren12 for coverage
CDR_FILES = [f"epstein_ren{i}.txt" for i in range(2, 13)]

# Phone number patterns
PHONE_RE = re.compile(
    r'(?:'
    r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'      # xxx-xxx-xxxx
    r'|'
    r'\b\d{10,11}\b'                              # 10-11 digit sequences
    r'|'
    r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}'             # (xxx) xxx-xxxx
    r'|'
    r'\b1?\d{3}\d{7}\b'                           # 1xxxxxxxxxx
    r')'
)

# Florida area codes
FL_AREA_CODES = {"239", "305", "321", "352", "386", "407", "561", "727", "754", "772", "786", "813", "850", "863", "904", "941", "954"}
# New York area codes
NY_AREA_CODES = {"212", "315", "347", "516", "518", "585", "607", "631", "646", "716", "718", "845", "914", "917", "929"}
# US Virgin Islands
VI_AREA_CODES = {"340"}
# New Mexico
NM_AREA_CODES = {"505", "575"}

def normalize_phone(raw):
    """Strip to digits only."""
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    if len(digits) != 10:
        return None
    # Skip obvious non-phones (all same digit, starts with 0)
    if len(set(digits)) <= 2:
        return None
    if digits[0] == '0':
        return None
    return digits

def area_code_location(digits):
    """Identify location from area code."""
    ac = digits[:3]
    if ac in FL_AREA_CODES:
        return "Florida"
    if ac in NY_AREA_CODES:
        return "New York"
    if ac in VI_AREA_CODES:
        return "USVI"
    if ac in NM_AREA_CODES:
        return "New Mexico"
    return "Other"

def format_phone(digits):
    """Format as (xxx) xxx-xxxx."""
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

# EFTA markers
def build_markers(content):
    return [(m.start(), int(m.group(1))) for m in re.finditer(r"EFTA(\d{5,8})", content)]

def pos_to_efta(pos, markers):
    best = None
    for mpos, mnum in markers:
        if mpos <= pos:
            best = mnum + 1
        else:
            break
    return best

def main():
    phone_data = defaultdict(lambda: {
        "count": 0, "files": set(), "locations": set(),
        "efta_pages": set(), "contexts": [],
    })

    for ocr_file in CDR_FILES:
        filepath = os.path.join(OCR_DIR, ocr_file)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        markers = build_markers(content)

        for m in PHONE_RE.finditer(content):
            digits = normalize_phone(m.group())
            if not digits:
                continue

            pos = m.start()
            efta = pos_to_efta(pos, markers)
            location = area_code_location(digits)

            phone_data[digits]["count"] += 1
            phone_data[digits]["files"].add(ocr_file)
            phone_data[digits]["locations"].add(location)
            if efta:
                phone_data[digits]["efta_pages"].add(efta)

            # Only store first 3 contexts per number
            if len(phone_data[digits]["contexts"]) < 3:
                ctx_start = max(0, pos - 100)
                ctx_end = min(len(content), pos + 20 + 100)
                ctx = content[ctx_start:ctx_end].replace("\n", " ").strip()
                phone_data[digits]["contexts"].append({
                    "file": ocr_file,
                    "efta": efta,
                    "text": ctx[:200],
                })

    print(f"Found {len(phone_data)} unique phone numbers.\n")

    # Convert sets to lists for JSON
    phone_list = []
    for digits, data in phone_data.items():
        phone_list.append({
            "number": format_phone(digits),
            "digits": digits,
            "count": data["count"],
            "files": sorted(data["files"]),
            "locations": sorted(data["locations"]),
            "efta_pages": sorted(data["efta_pages"]),
            "contexts": data["contexts"],
        })

    phone_list.sort(key=lambda x: -x["count"])

    # Save JSON
    with open(os.path.join(OUT_DIR, "phone_patterns.json"), "w") as f:
        json.dump(phone_list, f, indent=2, ensure_ascii=False)

    # Cross-location numbers (appear in both FL and NY)
    cross_location = [p for p in phone_list if len(p["locations"]) > 1 and p["count"] >= 3]
    fl_ny = [p for p in phone_list
             if "Florida" in p["locations"] and "New York" in p["locations"]]

    # Multi-file numbers
    multi_file = [p for p in phone_list if len(p["files"]) >= 3]

    # Build text output
    lines = [
        "PHONE PATTERN ANALYSIS",
        f"Total unique phone numbers: {len(phone_list)}",
        f"Numbers appearing 5+ times: {sum(1 for p in phone_list if p['count'] >= 5)}",
        f"Cross-location numbers: {len(cross_location)}",
        f"Florida ↔ New York numbers: {len(fl_ny)}",
        f"Numbers in 3+ files: {len(multi_file)}",
        "",
        "=" * 80,
        "TOP 30 MOST FREQUENT NUMBERS",
        "=" * 80,
        "",
    ]

    for p in phone_list[:30]:
        lines.append(f"  {p['number']:<18} count={p['count']:<5} loc={','.join(p['locations']):<20} files={len(p['files'])}")
        if p["contexts"]:
            lines.append(f"    ...{p['contexts'][0]['text'][:120]}...")
        lines.append("")

    lines.extend([
        "=" * 80,
        "CROSS-LOCATION NUMBERS (appear in multiple geographic areas)",
        "=" * 80,
        "",
    ])

    for p in cross_location[:20]:
        lines.append(f"  {p['number']:<18} count={p['count']:<5} locations: {', '.join(p['locations'])}")
        lines.append(f"    Files: {', '.join(p['files'])}")
        lines.append("")

    if fl_ny:
        lines.extend([
            "=" * 80,
            "FLORIDA ↔ NEW YORK NUMBERS (connected to both Epstein residences)",
            "=" * 80,
            "",
        ])
        for p in fl_ny[:15]:
            lines.append(f"  {p['number']:<18} count={p['count']:<5}")
            lines.append(f"    Files: {', '.join(p['files'])}")
            lines.append("")

    # Area code distribution
    ac_counts = Counter()
    for p in phone_list:
        ac = p["digits"][:3]
        ac_counts[ac] += p["count"]

    lines.extend([
        "=" * 80,
        "AREA CODE DISTRIBUTION (by total call count)",
        "=" * 80,
        "",
    ])
    for ac, count in ac_counts.most_common(20):
        loc = area_code_location(ac + "0000000")
        lines.append(f"  ({ac}) — {count:>6} calls — {loc}")

    text = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "phone_patterns.txt"), "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
