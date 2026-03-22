#!/usr/bin/env python3
"""
Money trail analysis: extract dollar amounts, dates, payers/recipients from OCR files.
Focus on ren16.txt and ren17.txt (prosecution memos) but scan all files.

Output: money_trail.json, money_trail.txt
"""

import json
import os
import re
from collections import defaultdict

OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Known event dates for correlation
EVENTS = [
    ("2018-11-01", "Miami Herald coverage begins"),
    ("2019-07-06", "Epstein arrested"),
    ("2019-08-10", "Epstein death"),
    ("2019-07-25", "Wexner proffer"),
    ("2023-05-26", "Leon Black HT referral"),
    ("2005-03-01", "Palm Beach police investigation begins"),
    ("2007-06-30", "NPA signed"),
    ("2008-01-01", "Wexner $100M settlement"),
]

# EFTA marker mapping
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

# Dollar amount patterns
MONEY_RE = re.compile(
    r'(?:'
    r'\$\s?[\d,]+(?:\.\d{1,2})?(?:\s?(?:million|billion|thousand|M|B|K))?'
    r'|'
    r'(?:[\d,]+(?:\.\d{1,2})?)\s?(?:dollars|million\s?dollars|billion\s?dollars)'
    r'|'
    r'\$[\d,]+(?:\.\d{1,2})?'
    r')',
    re.IGNORECASE,
)

# Date patterns
DATE_RE = re.compile(
    r'(?:'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2},?\s+\d{4}'
    r'|'
    r'\d{1,2}/\d{1,2}/\d{2,4}'
    r'|'
    r'(?:early|late|mid)?\s?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
    r'|'
    r'(?:in|around|circa|approximately)\s+\d{4}'
    r'|'
    r'\b(?:19|20)\d{2}\b'
    r')',
    re.IGNORECASE,
)

# Names to look for near payments
NAMES_RE = re.compile(
    r'\b(?:Epstein|Maxwell|Groff|Indyke|Kahn|Wexner|Black|Staley|Dubin|'
    r'Brunel|Kellen|Marcinkova|Alvarez|Galindo|Klein|Rodriguez|'
    r'Deutsche Bank|JP Morgan|Bear Stearns|Southern Trust|Financial Trust|'
    r'Apollo|Wigdor|Christensen|Edwards)\b',
    re.IGNORECASE,
)

def normalize_amount(text):
    """Convert amount text to a numeric value."""
    text = text.strip().replace(",", "").replace("$", "").strip()
    multiplier = 1
    for suffix, mult in [("billion", 1_000_000_000), ("million", 1_000_000),
                          ("thousand", 1_000), ("B", 1_000_000_000),
                          ("M", 1_000_000), ("K", 1_000)]:
        if suffix.lower() in text.lower():
            text = re.sub(r'(?i)\s*' + suffix, '', text).strip()
            multiplier = mult
            break
    try:
        return float(text) * multiplier
    except (ValueError, TypeError):
        return None

def find_nearby_date(content, pos, window=500):
    """Find the nearest date within window chars of position."""
    start = max(0, pos - window)
    end = min(len(content), pos + window)
    chunk = content[start:end]
    dates = list(DATE_RE.finditer(chunk))
    if not dates:
        return None
    # Find closest to the money reference
    center = pos - start
    closest = min(dates, key=lambda m: abs(m.start() - center))
    return closest.group().strip()

def find_nearby_names(content, pos, window=300):
    """Find person/entity names near the amount."""
    start = max(0, pos - window)
    end = min(len(content), pos + window)
    chunk = content[start:end]
    return list(set(m.group() for m in NAMES_RE.finditer(chunk)))

def main():
    transactions = []
    # Prioritize ren16 and ren17 but scan all
    ocr_files = sorted(f for f in os.listdir(OCR_DIR) if f.startswith("epstein_ren") and f.endswith(".txt"))

    for ocr_file in ocr_files:
        filepath = os.path.join(OCR_DIR, ocr_file)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        markers = build_markers(content)

        for m in MONEY_RE.finditer(content):
            amount_text = m.group().strip()
            amount_val = normalize_amount(amount_text)
            if amount_val is None or amount_val < 100:
                continue  # Skip trivially small amounts

            pos = m.start()
            efta = pos_to_efta(pos, markers)
            date = find_nearby_date(content, pos)
            names = find_nearby_names(content, pos)

            # Context
            ctx_start = max(0, pos - 150)
            ctx_end = min(len(content), pos + len(amount_text) + 150)
            context = content[ctx_start:ctx_end].replace("\n", " ").strip()

            transactions.append({
                "amount_text": amount_text,
                "amount_value": amount_val,
                "date": date,
                "names": names,
                "file": ocr_file,
                "efta_page": efta,
                "context": context[:300],
            })

    print(f"Found {len(transactions)} financial references across all files.\n")

    # Sort by amount descending for JSON
    transactions.sort(key=lambda x: -(x["amount_value"] or 0))

    # Save JSON
    with open(os.path.join(OUT_DIR, "money_trail.json"), "w") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

    # Build readable text output
    lines = [
        "MONEY TRAIL ANALYSIS",
        f"Total financial references found: {len(transactions)}",
        "",
        "=" * 80,
        "LARGEST AMOUNTS",
        "=" * 80,
        "",
    ]

    for t in transactions[:30]:
        efta_str = f"EFTA{t['efta_page']:08d}" if t.get("efta_page") else "unknown"
        lines.append(f"  {t['amount_text']:<25} {efta_str}  {t['file']}")
        if t["date"]:
            lines.append(f"    Date: {t['date']}")
        if t["names"]:
            lines.append(f"    Names: {', '.join(t['names'])}")
        lines.append(f"    ...{t['context'][:150]}...")
        lines.append("")

    # Payments in prosecution memos (ren16, ren17) sorted by date
    memo_txns = [t for t in transactions if t["file"] in ("epstein_ren16.txt", "epstein_ren17.txt")]
    dated_txns = [t for t in memo_txns if t.get("date")]

    lines.extend([
        "=" * 80,
        f"PROSECUTION MEMO PAYMENTS (ren16 + ren17): {len(memo_txns)} total, {len(dated_txns)} with dates",
        "=" * 80,
        "",
    ])

    for t in dated_txns:
        efta_str = f"EFTA{t['efta_page']:08d}" if t.get("efta_page") else "?"
        lines.append(f"  {t['date']:<30} {t['amount_text']:<20} {efta_str}")
        if t["names"]:
            lines.append(f"    Names: {', '.join(t['names'])}")
        lines.append("")

    # Event correlation
    lines.extend([
        "=" * 80,
        "EVENT CORRELATION",
        "=" * 80,
        "",
    ])

    # Look for payments mentioning specific events
    for event_date, event_name in EVENTS:
        year = event_date[:4]
        matches = [t for t in memo_txns
                   if t.get("date") and year in str(t["date"])
                   and t["amount_value"] and t["amount_value"] >= 1000]
        if matches:
            lines.append(f"  {event_name} ({event_date}):")
            for t in matches[:5]:
                lines.append(f"    {t['amount_text']} — {t.get('date', '?')}")
            lines.append("")

    # Summary stats
    amounts = [t["amount_value"] for t in transactions if t["amount_value"]]
    lines.extend([
        "=" * 80,
        "SUMMARY",
        "=" * 80,
        f"  Total references: {len(transactions)}",
        f"  In prosecution memos: {len(memo_txns)}",
        f"  With dates: {len(dated_txns)}",
        f"  Amounts range: ${min(amounts):,.0f} to ${max(amounts):,.0f}" if amounts else "",
        f"  Amounts > $100K: {sum(1 for a in amounts if a >= 100_000)}",
        f"  Amounts > $1M: {sum(1 for a in amounts if a >= 1_000_000)}",
    ])

    text = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "money_trail.txt"), "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
