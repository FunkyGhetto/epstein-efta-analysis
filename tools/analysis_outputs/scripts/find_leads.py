#!/usr/bin/env python3
"""
Lead Finder — Systematically identifies unresolved threads, contradictions,
and unexplored connections across OCR files and analysis documents.
"""

import os
import re
import json
import glob
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OCR_DIR = os.path.join(REPO, "ocr")
ANALYSIS_DIR = os.path.join(REPO, "analysis")
DATA_DIR = os.path.join(REPO, "tools", "analysis_outputs", "data")
ENTITY_DIR = os.path.join(REPO, "tools", "entity_network", "data")
RHOWARDSTONE = os.path.expanduser("~/Documents/Epstein-research")

leads = []


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_analysis_text():
    """All analysis .md files concatenated."""
    texts = []
    for f in glob.glob(os.path.join(ANALYSIS_DIR, "*.md")):
        texts.append(read_file(f))
    texts.append(read_file(os.path.join(REPO, "README.md")))
    return '\n'.join(texts)


def get_efta_page(lines, line_idx):
    """Find the corrected EFTA page for a given line using off-by-one rule.
    Search forward from line_idx for the next EFTA marker — that's the correct page."""
    for i in range(line_idx, min(line_idx + 150, len(lines))):
        m = re.search(r'EFTA(\d{7,8})', lines[i])
        if m:
            return m.group(1)
    # Fallback: search backward
    for i in range(line_idx, max(line_idx - 150, 0), -1):
        m = re.search(r'EFTA(\d{7,8})', lines[i])
        if m:
            num = int(m.group(1))
            return str(num + 1).zfill(len(m.group(1)))
    return "unknown"


def get_context(lines, line_idx, chars=200):
    """Get surrounding context."""
    start = max(0, line_idx - 3)
    end = min(len(lines), line_idx + 4)
    ctx = ' '.join(lines[start:end]).strip()
    if len(ctx) > chars:
        # Center on the target line
        target = lines[line_idx]
        pos = ctx.find(target)
        if pos > chars // 2:
            ctx = '...' + ctx[pos - chars // 4:]
        if len(ctx) > chars:
            ctx = ctx[:chars] + '...'
    return re.sub(r'\s+', ' ', ctx)


def add_lead(category, text, efta_page, ocr_file, line, priority, note):
    leads.append({
        "category": category,
        "text": text,
        "efta_page": efta_page,
        "ocr_file": ocr_file,
        "line": line,
        "priority": priority,
        "note": note
    })


# ============================================================
# 1. UNRESOLVED QUESTIONS
# ============================================================
def find_unresolved():
    print("1. Searching for unresolved questions...")
    patterns = [
        (r'we are continuing|continuing to (?:receive|review|investigate|analyze)',
         "Ongoing investigation thread"),
        (r'we plan to (?:request|interview|approach|contact|meet)',
         "Planned action — may or may not have occurred"),
        (r'we have not yet|not yet (?:identified|been able|interviewed|received)',
         "Unresolved investigative gap"),
        (r'we are in the process of',
         "In-progress action"),
        (r'remains? outstanding|remains? open',
         "Outstanding item"),
        (r'further investigation|further analysis|additional investigation',
         "Further investigation flagged"),
        (r'awaiting (?:response|results|documents|records)',
         "Awaiting external input"),
        (r'intend to approach|plan to hold off|after charging',
         "Post-charging plan"),
    ]

    for ocr_name in ['epstein_ren16.txt', 'epstein_ren17.txt']:
        ocr_path = os.path.join(OCR_DIR, ocr_name)
        if not os.path.exists(ocr_path):
            continue
        text = read_file(ocr_path)
        lines = text.split('\n')

        for pattern, note_base in patterns:
            for i, line in enumerate(lines):
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    efta = get_efta_page(lines, i)
                    ctx = get_context(lines, i, 250)

                    # Score priority
                    if re.search(r'plan to (?:request|interview|approach)', line, re.IGNORECASE):
                        priority = "high"
                        note = f"SDNY planned action: {note_base}"
                    elif re.search(r'not yet|awaiting', line, re.IGNORECASE):
                        priority = "medium"
                        note = note_base
                    else:
                        priority = "low"
                        note = note_base

                    add_lead("unresolved_question", ctx, efta, ocr_name, i + 1, priority, note)

    count = sum(1 for l in leads if l['category'] == 'unresolved_question')
    print(f"   Found {count} unresolved threads")


# ============================================================
# 2. NAMED BUT UNEXPLORED PEOPLE
# ============================================================
def find_unexplored_people():
    print("2. Searching for named but unexplored people...")

    entities_path = os.path.join(ENTITY_DIR, "entities.json")
    if not os.path.exists(entities_path):
        print("   Skipped: entities.json not found")
        return

    with open(entities_path) as f:
        entities = json.load(f)

    analysis_text = get_analysis_text().lower()

    # Keywords that indicate criminal relevance
    crime_keywords = {'massage', 'minor', 'sexual', 'recruit', 'abuse', 'rape',
                      'victim', 'underage', 'traffick', 'lent out'}

    flagged_path = os.path.join(ENTITY_DIR, "flagged.json")
    flagged_names = set()
    if os.path.exists(flagged_path):
        with open(flagged_path) as f:
            flagged_data = json.load(f)
        if isinstance(flagged_data, list):
            for entry in flagged_data:
                if isinstance(entry, dict):
                    flagged_names.add(entry.get('name', '').lower())
                elif isinstance(entry, str):
                    flagged_names.add(entry.lower())

    # Known names we already discuss
    known_names = {'epstein', 'maxwell', 'dubin', 'weinstein', 'black', 'staley',
                   'indyke', 'groff', 'blaine', 'wexner', 'andrew', 'dershowitz',
                   'brunel', 'kahn', 'alessi', 'copperfield', 'acosta'}

    unexplored = []
    for name, info in entities.items():
        name_lower = name.lower()
        # Skip if already in our analysis or a known name
        if any(k in name_lower for k in known_names):
            continue
        if name_lower in analysis_text:
            continue

        # Check if flagged by keyword proximity
        if name_lower in flagged_names:
            # Check occurrences for crime-keyword context
            has_crime_context = False
            sample_context = ""
            sample_efta = "unknown"
            sample_file = ""
            sample_line = 0

            if 'occurrences' in info:
                for occ in info['occurrences']:
                    ctx = occ.get('context', '').lower()
                    if any(kw in ctx for kw in crime_keywords):
                        has_crime_context = True
                        sample_context = occ.get('context', '')[:200]
                        sample_efta = occ.get('efta_page', 'unknown')
                        sample_file = occ.get('file', '')
                        sample_line = occ.get('line', 0)
                        break

            if has_crime_context:
                priority = "high"
                note = f"Flagged name near crime keywords, not in any analysis file"
            else:
                priority = "low"
                note = f"Flagged name but no direct crime context found"

            add_lead("unexplored_person", f"{name}: {sample_context}",
                     sample_efta, sample_file, sample_line, priority, note)
            unexplored.append(name)

    count = sum(1 for l in leads if l['category'] == 'unexplored_person')
    print(f"   Found {count} unexplored flagged people")


# ============================================================
# 3. CONTRADICTIONS
# ============================================================
def find_contradictions():
    print("3. Searching for contradictions and inconsistencies...")
    patterns = [
        (r'inconsistent with', "Testimony inconsistency noted by SDNY"),
        (r'contrary to', "Contradiction noted by SDNY"),
        (r'does not recall.*(?:claim|stat|said|told|describ)',
         "Memory gap on a specific claim"),
        (r'(?:claim|stat|said|told).*does not recall',
         "Memory gap on a specific claim"),
        (r'however.*(?:evidence|investigation|review|record)',
         "Evidentiary qualification"),
        (r'we note that', "Prosecutorial note — often a red flag"),
        (r'disputed?\s+(?:this|that|the|her|his)',
         "Active dispute of testimony"),
        (r'publicly denied', "Public denial of allegation"),
        (r'unable to (?:corroborate|confirm|verify)',
         "Corroboration failure"),
    ]

    for ocr_name in ['epstein_ren16.txt', 'epstein_ren17.txt']:
        ocr_path = os.path.join(OCR_DIR, ocr_name)
        if not os.path.exists(ocr_path):
            continue
        text = read_file(ocr_path)
        lines = text.split('\n')

        for pattern, note_base in patterns:
            for i, line in enumerate(lines):
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    efta = get_efta_page(lines, i)
                    ctx = get_context(lines, i, 250)

                    if 'inconsistent' in line.lower() or 'unable to corroborate' in line.lower():
                        priority = "medium"
                    elif 'publicly denied' in line.lower():
                        priority = "medium"
                    else:
                        priority = "low"

                    add_lead("contradiction", ctx, efta, ocr_name, i + 1,
                             priority, note_base)

    count = sum(1 for l in leads if l['category'] == 'contradiction')
    print(f"   Found {count} contradictions/inconsistencies")


# ============================================================
# 4. UNCITED FINANCIAL TRANSACTIONS
# ============================================================
def find_uncited_money():
    print("4. Searching for uncited financial transactions...")

    money_path = os.path.join(DATA_DIR, "money_trail.json")
    if not os.path.exists(money_path):
        print("   Skipped: money_trail.json not found")
        return

    with open(money_path) as f:
        money_data = json.load(f)

    analysis_text = get_analysis_text()

    # Get all EFTA numbers cited in analysis
    cited_efta = set(re.findall(r'EFTA(\d{5,8})', analysis_text))

    uncited = 0
    transactions = money_data if isinstance(money_data, list) else money_data.get('transactions', [])
    for tx in transactions:
        efta = tx.get('efta_page', tx.get('efta', ''))
        if isinstance(efta, str):
            efta_num = re.sub(r'[^0-9]', '', efta)
        else:
            efta_num = str(efta)

        if efta_num and efta_num not in cited_efta:
            amount = tx.get('amount', tx.get('text', 'unknown amount'))
            context = tx.get('context', tx.get('text', ''))[:200]

            # Higher priority for large amounts
            if any(kw in str(amount).lower() for kw in ['million', '000,000', '00000']):
                priority = "medium"
            else:
                priority = "low"

            add_lead("uncited_financial", f"{amount}: {context}",
                     efta_num, tx.get('file', ''), tx.get('line', 0),
                     priority, "Financial transaction not cited in analysis")
            uncited += 1

    print(f"   Found {uncited} uncited financial references")


# ============================================================
# 5. CROSS-REFERENCE GAPS WITH RHOWARDSTONE
# ============================================================
def find_rhowardstone_gaps():
    print("5. Checking rhowardstone cross-reference gaps...")

    if not os.path.exists(RHOWARDSTONE):
        print("   Skipped: rhowardstone repo not found")
        return

    # Find all their files that reference our main memo
    our_memo_refs = []
    for md_path in glob.glob(os.path.join(RHOWARDSTONE, "**", "*.md"), recursive=True):
        text = read_file(md_path)
        if '02731082' in text:
            our_memo_refs.append(md_path)

    analysis_text = get_analysis_text().lower()

    gaps = 0
    for ref_path in our_memo_refs:
        text = read_file(ref_path)
        basename = os.path.basename(ref_path)

        # Find page numbers they cite from our memo that we don't discuss
        their_pages = set()
        for m in re.finditer(r'02731\d{3}', text):
            their_pages.add(m.group(0))

        our_pages = set(re.findall(r'02731\d{3}', analysis_text))
        their_only = their_pages - our_pages

        if their_only:
            # Check what they discuss on those pages
            for page in sorted(their_only):
                # Get context around the page reference in their file
                page_idx = text.find(page)
                if page_idx >= 0:
                    ctx_start = max(0, page_idx - 100)
                    ctx_end = min(len(text), page_idx + 200)
                    ctx = text[ctx_start:ctx_end].replace('\n', ' ').strip()

                    add_lead("rhowardstone_gap",
                             f"{basename}: page {page} — {ctx[:200]}",
                             page, basename, 0, "medium",
                             f"rhowardstone discusses EFTA{page} from our memo but we don't cite it")
                    gaps += 1

    print(f"   Found {gaps} pages discussed by rhowardstone but not in our analysis")


# ============================================================
# 6. UNCOVERED VICTIM SECTIONS
# ============================================================
def find_uncovered_victims():
    print("6. Searching for uncovered victim interviews...")

    patterns = [
        (r'was interviewed (?:in|on|via|by)', "Victim/witness interview"),
        (r'reported being sexually (?:abused|assaulted|trafficked)', "Sexual abuse report"),
        (r'proffer', "Attorney proffer"),
        (r'On (?:August|September|October|November|July) \d+, 2019.*(?:interview|met with)',
         "Post-arrest interview (July-Nov 2019)"),
    ]

    # Get EFTA pages we already cover in victim cross-reference
    vcr_path = os.path.join(ANALYSIS_DIR, "victim-cross-reference-english.md")
    covered_pages = set()
    if os.path.exists(vcr_path):
        vcr_text = read_file(vcr_path)
        covered_pages = set(re.findall(r'02731\d{3}', vcr_text))

    for ocr_name in ['epstein_ren16.txt', 'epstein_ren17.txt']:
        ocr_path = os.path.join(OCR_DIR, ocr_name)
        if not os.path.exists(ocr_path):
            continue
        text = read_file(ocr_path)
        lines = text.split('\n')

        for pattern, note_base in patterns:
            for i, line in enumerate(lines):
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    efta = get_efta_page(lines, i)

                    # Skip if we already cover this page
                    if efta in covered_pages:
                        continue

                    ctx = get_context(lines, i, 250)

                    # Check if this looks like a new victim section
                    if 'sexually' in line.lower() or 'trafficked' in line.lower():
                        priority = "high"
                        note = f"Uncovered victim account: {note_base}"
                    elif 'proffer' in line.lower():
                        priority = "medium"
                        note = f"Uncovered proffer: {note_base}"
                    else:
                        priority = "low"
                        note = note_base

                    add_lead("uncovered_victim", ctx, efta, ocr_name, i + 1,
                             priority, note)

    count = sum(1 for l in leads if l['category'] == 'uncovered_victim')
    print(f"   Found {count} uncovered victim/interview sections")


# ============================================================
# DEDUPLICATE AND OUTPUT
# ============================================================
def deduplicate():
    """Remove near-duplicate leads (same EFTA page + same category)."""
    seen = set()
    unique = []
    for lead in leads:
        key = (lead['category'], lead['efta_page'], lead['line'])
        if key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique


def write_output(leads_final):
    # Sort by priority then category
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    leads_final.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['category']))

    # JSON
    json_path = os.path.join(DATA_DIR, "leads.json")
    with open(json_path, 'w') as f:
        json.dump({"total": len(leads_final), "leads": leads_final}, f, indent=2)

    # Human-readable text
    txt_path = os.path.join(DATA_DIR, "leads.txt")
    with open(txt_path, 'w') as f:
        f.write("LEAD FINDER — UNRESOLVED THREADS AND GAPS\n")
        f.write("=" * 60 + "\n\n")

        counts = {}
        for l in leads_final:
            counts[l['priority']] = counts.get(l['priority'], 0) + 1

        f.write(f"Total leads: {len(leads_final)}\n")
        f.write(f"  HIGH: {counts.get('high', 0)}\n")
        f.write(f"  MEDIUM: {counts.get('medium', 0)}\n")
        f.write(f"  LOW: {counts.get('low', 0)}\n\n")

        current_priority = None
        for i, lead in enumerate(leads_final, 1):
            if lead['priority'] != current_priority:
                current_priority = lead['priority']
                f.write(f"\n{'=' * 60}\n")
                f.write(f"  {current_priority.upper()} PRIORITY\n")
                f.write(f"{'=' * 60}\n\n")

            f.write(f"[{i}] {lead['category'].upper()} — EFTA{lead['efta_page']}\n")
            f.write(f"    File: {lead['ocr_file']} line {lead['line']}\n")
            f.write(f"    Note: {lead['note']}\n")
            f.write(f"    Text: {lead['text'][:300]}\n\n")

    return json_path, txt_path


def main():
    print("=" * 60)
    print("LEAD FINDER — Unresolved Threads and Gaps")
    print("=" * 60 + "\n")

    find_unresolved()
    find_unexplored_people()
    find_contradictions()
    find_uncited_money()
    find_rhowardstone_gaps()
    find_uncovered_victims()

    leads_final = deduplicate()

    json_path, txt_path = write_output(leads_final)

    # Summary
    priority_counts = {}
    category_counts = {}
    for l in leads_final:
        priority_counts[l['priority']] = priority_counts.get(l['priority'], 0) + 1
        category_counts[l['category']] = category_counts.get(l['category'], 0) + 1

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {len(leads_final)} total leads")
    print(f"{'=' * 60}")
    print(f"  HIGH:   {priority_counts.get('high', 0)}")
    print(f"  MEDIUM: {priority_counts.get('medium', 0)}")
    print(f"  LOW:    {priority_counts.get('low', 0)}")
    print(f"\nBy category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print(f"\nOutput: {json_path}")
    print(f"Output: {txt_path}")

    # Print top HIGH leads
    high_leads = [l for l in leads_final if l['priority'] == 'high']
    if high_leads:
        print(f"\n{'=' * 60}")
        print(f"TOP {min(20, len(high_leads))} HIGH PRIORITY LEADS")
        print(f"{'=' * 60}")
        for i, lead in enumerate(high_leads[:20], 1):
            print(f"\n[{i}] {lead['category'].upper()} — EFTA{lead['efta_page']}")
            print(f"    {lead['ocr_file']} line {lead['line']}")
            print(f"    {lead['note']}")
            print(f"    {lead['text'][:200]}")


if __name__ == "__main__":
    main()
