#!/usr/bin/env python3
"""
Redaction pattern analysis for prosecution memos (ren16.txt, ren17.txt).
Identifies redaction gaps, measures lengths, groups by pattern, and
cross-references with victim identifiers.

Output: redaction_analysis.json, redaction_analysis.txt
"""

import json
import os
import re
from collections import defaultdict, Counter

OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

MEMO_FILES = ["epstein_ren16.txt", "epstein_ren17.txt"]

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

# Patterns that indicate a redacted name
# In OCR, redactions appear as blank spaces, single characters, or [REDACTED]
REDACTION_PATTERNS = [
    # Explicit redaction markers
    (r'\[REDACTED\]', "explicit_redacted"),
    (r'\[redacted\]', "explicit_redacted"),
    (r'REDACTED', "explicit_redacted"),
    # Single/double letter fragments where a name should be (with context)
    (r'(?:Maxwell|Epstein|Groff)\s+(?:told|instructed|directed|asked)\s+([a-z]{1,3})\s+to\b', "action_target"),
    (r'(?:told|instructed|directed|asked)\s+([a-z]{1,3})\s+to\b', "action_target"),
    (r'\b([a-z]{1,3})\s+(?:recalled|described|testified|stated|explained|reported)\b', "subject_verb"),
    (r'\b([a-z]{1,3})\s+(?:was\s+(?:interviewed|recruited|introduced|directed|instructed|paid|given))', "passive_subject"),
    (r'(?:victim|massage|sex|sexual)\s+(?:with|to|from|for)\s+([a-z]{1,3})\b', "victim_ref"),
    # Blanks/spaces in name position
    (r'(?:named|called|known as)\s{2,}(?=\w)', "blank_name"),
]

# Victim identifier patterns
VICTIM_RE = re.compile(
    r'(?:Victim[- ]?\d+|victim[- ]?\d+|VICTIM[- ]?\d+|'
    r'Minor[- ]?\d+|minor[- ]?\d+|'
    r'Jane Doe[- ]?\d*|John Doe[- ]?\d*|'
    r'Victim \w+)',
    re.IGNORECASE,
)


def main():
    all_redactions = []
    gap_lengths = Counter()
    gap_contexts = defaultdict(list)  # gap_length → list of contexts
    victim_redaction_map = defaultdict(list)  # victim_id → list of redaction patterns
    fragment_counts = Counter()  # count each fragment (ia, iz, etc.)

    for ocr_file in MEMO_FILES:
        filepath = os.path.join(OCR_DIR, ocr_file)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        markers = build_markers(content)

        # 1. Find explicit [REDACTED] markers
        for m in re.finditer(r'\[?REDACTED\]?', content, re.IGNORECASE):
            pos = m.start()
            efta = pos_to_efta(pos, markers)
            ctx_start = max(0, pos - 100)
            ctx_end = min(len(content), pos + len(m.group()) + 100)
            context = content[ctx_start:ctx_end].replace("\n", " ").strip()

            # Check for nearby victim identifier
            nearby = content[max(0, pos - 300):min(len(content), pos + 300)]
            victim_matches = VICTIM_RE.findall(nearby)
            victim_id = victim_matches[0] if victim_matches else None

            all_redactions.append({
                "type": "explicit",
                "text": m.group(),
                "gap_length": len(m.group()),
                "file": ocr_file,
                "efta_page": efta,
                "context": context[:250],
                "victim_id": victim_id,
            })

            gap_lengths[len(m.group())] += 1
            if victim_id:
                victim_redaction_map[victim_id].append({
                    "type": "explicit",
                    "efta": efta,
                    "context": context[:150],
                })

        # 2. Find single/double letter fragments in name positions
        # These are OCR renders of redacted names
        fragment_re = re.compile(r'\b([a-z]{1,3})\b')
        for m in fragment_re.finditer(content):
            frag = m.group(1)
            # Only count if surrounded by context suggesting a name position
            pos = m.start()
            before = content[max(0, pos - 50):pos].strip()
            after = content[pos + len(frag):min(len(content), pos + len(frag) + 50)].strip()

            # Check if fragment is in a name-like position
            is_name_pos = False
            # After a verb that takes a person object
            if re.search(r'(?:told|instructed|directed|asked|paid|gave|introduced|recruited|called)\s*$', before):
                is_name_pos = True
            # Before a verb that takes a person subject
            if re.search(r'^(?:\s*(?:recalled|described|testified|stated|explained|was|did|went|began|had|felt|ran|complained))', after):
                is_name_pos = True
            # After possessive context
            if re.search(r"(?:'s|Maxwell|Epstein|Groff)\s*$", before):
                is_name_pos = True

            if is_name_pos:
                efta = pos_to_efta(pos, markers)
                ctx_start = max(0, pos - 80)
                ctx_end = min(len(content), pos + len(frag) + 80)
                context = content[ctx_start:ctx_end].replace("\n", " ").strip()

                nearby = content[max(0, pos - 300):min(len(content), pos + 300)]
                victim_matches = VICTIM_RE.findall(nearby)
                victim_id = victim_matches[0] if victim_matches else None

                fragment_counts[frag] += 1

                all_redactions.append({
                    "type": "fragment",
                    "text": frag,
                    "gap_length": len(frag),
                    "file": ocr_file,
                    "efta_page": efta,
                    "context": context[:250],
                    "victim_id": victim_id,
                })

                if victim_id:
                    victim_redaction_map[victim_id].append({
                        "type": f"fragment:{frag}",
                        "efta": efta,
                        "context": context[:150],
                    })

    print(f"Found {len(all_redactions)} redaction instances.\n")

    # Save JSON
    output = {
        "total_redactions": len(all_redactions),
        "explicit_count": sum(1 for r in all_redactions if r["type"] == "explicit"),
        "fragment_count": sum(1 for r in all_redactions if r["type"] == "fragment"),
        "top_fragments": fragment_counts.most_common(30),
        "victim_map": {k: v for k, v in victim_redaction_map.items()},
        "redactions": all_redactions[:500],  # Cap for file size
    }

    with open(os.path.join(OUT_DIR, "redaction_analysis.json"), "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Group fragments by which EFTA pages they appear on
    fragment_pages = defaultdict(set)
    for r in all_redactions:
        if r["type"] == "fragment" and r.get("efta_page"):
            fragment_pages[r["text"]].add(r["efta_page"])

    # Find fragments that likely represent the same person
    # (appear on many of the same pages)
    fragment_groups = defaultdict(set)
    frags = list(fragment_pages.keys())
    for i in range(len(frags)):
        for j in range(i + 1, len(frags)):
            pages_i = fragment_pages[frags[i]]
            pages_j = fragment_pages[frags[j]]
            if not pages_i or not pages_j:
                continue
            overlap = len(pages_i & pages_j)
            total = min(len(pages_i), len(pages_j))
            if total >= 3 and overlap / total >= 0.5:
                fragment_groups[frags[i]].add(frags[j])
                fragment_groups[frags[j]].add(frags[i])

    # Build text output
    lines = [
        "REDACTION PATTERN ANALYSIS",
        f"Files analyzed: {', '.join(MEMO_FILES)}",
        f"Total redaction instances: {len(all_redactions)}",
        f"  Explicit [REDACTED]: {output['explicit_count']}",
        f"  OCR fragments in name positions: {output['fragment_count']}",
        "",
        "=" * 80,
        "TOP 30 REDACTION FRAGMENTS (OCR renders of redacted names)",
        "=" * 80,
        "",
    ]

    for frag, count in fragment_counts.most_common(30):
        pages = sorted(fragment_pages.get(frag, set()))
        page_str = ", ".join(str(p) for p in pages[:10])
        if len(pages) > 10:
            page_str += f"... (+{len(pages)-10} more)"
        related = fragment_groups.get(frag, set())
        lines.append(f"  '{frag}' — {count} occurrences across {len(pages)} pages")
        if related:
            lines.append(f"    Co-occurs with: {', '.join(sorted(related))}")
        if page_str:
            lines.append(f"    Pages: {page_str}")
        lines.append("")

    # Fragment co-occurrence groups (likely same person)
    lines.extend([
        "=" * 80,
        "FRAGMENT GROUPS (fragments that appear on the same pages — likely same person)",
        "=" * 80,
        "",
    ])

    seen_groups = set()
    for frag, related in sorted(fragment_groups.items(), key=lambda x: -len(x[1])):
        group = frozenset({frag} | related)
        if group in seen_groups:
            continue
        seen_groups.add(group)
        group_pages = set()
        for f in group:
            group_pages |= fragment_pages.get(f, set())
        lines.append(f"  Group: {{{', '.join(sorted(group))}}}")
        lines.append(f"    Shared pages: {len(group_pages)}")
        lines.append("")

    # Victim-to-redaction mapping
    lines.extend([
        "=" * 80,
        "VICTIM ↔ REDACTION MAPPING",
        "=" * 80,
        "",
    ])

    for victim_id, redactions in sorted(victim_redaction_map.items()):
        lines.append(f"  {victim_id}: {len(redactions)} redaction instances")
        frag_types = Counter(r["type"] for r in redactions)
        for ft, cnt in frag_types.most_common(5):
            lines.append(f"    {ft}: {cnt}")
        # Show sample contexts
        for r in redactions[:3]:
            lines.append(f"    [{r.get('efta', '?')}] ...{r['context'][:100]}...")
        lines.append("")

    # EFTA pages with most redactions
    page_redaction_counts = Counter()
    for r in all_redactions:
        if r.get("efta_page"):
            page_redaction_counts[r["efta_page"]] += 1

    lines.extend([
        "=" * 80,
        "EFTA PAGES WITH MOST REDACTIONS",
        "=" * 80,
        "",
    ])
    for page, count in page_redaction_counts.most_common(20):
        lines.append(f"  EFTA{page:08d}: {count} redactions")

    text = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "redaction_analysis.txt"), "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
