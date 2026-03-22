#!/usr/bin/env python3
"""
Entity extraction from EFTA OCR files using SpaCy NER.
Produces entities.json, cooccurrence.json, and flagged.json.

Usage: python3 extract.py
"""

import json
import os
import re
import sys
from collections import defaultdict

import spacy

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

KEYWORDS = [
    "massage", "minor", "underage", "recruit", "payment", "wire",
    "rape", "raped", "lent out", "sexual", "abuse",
]

# Names to merge — map variant → canonical
ALIASES = {
    "Black": "Leon Black",
    "Epstein": "Jeffrey Epstein",
    "Jeff Epstein": "Jeffrey Epstein",
    "Maxwell": "Ghislaine Maxwell",
    "Groff": "Leslie Groff",
    "Lesley Groff": "Leslie Groff",
    "Indyke": "Darren Indyke",
    "Wexner": "Les Wexner",
    "Leslie Wexner": "Les Wexner",
    "Acosta": "Alexander Acosta",
    "R. Alexander Acosta": "Alexander Acosta",
    "Staley": "Jes Staley",
    "Brunel": "Jean-Luc Brunel",
    "Jean Luc Brunel": "Jean-Luc Brunel",
    "Dubin": "Glen Dubin",
    "Glen": "Glen Dubin",
    "Eva Dubin": "Glen Dubin",  # couple treated as unit
    "Dershowitz": "Alan Dershowitz",
    "Clinton": "Bill Clinton",
    "Prince Andrew": "Prince Andrew",
    "Andrew": "Prince Andrew",
    "Copperfield": "David Copperfield",
    "David Blane": "David Blaine",
    "Blaine": "David Blaine",
    "Blane": "David Blaine",
    "Kahn": "Rich Kahn",
    "Rodriguez": "Michelle Rodriguez",
    "Marcinkova": "Nadia Marcinkova",
    "Kellen": "Sarah Kellen",
    "Alvarez": "Joseph Alvarez",
    "Christensen": "Jeanne Christensen",
    "Klein": "Bella Klein",
    "Galindo": "Kimberly Galindo",
    "Noel": "Tova Noel",
    "Thomas": "Michael Thomas",
    "Harris": "Shahada Harris",
    "Edwards": "Brad Edwards",
    "Estrich": "Susan Estrich",
    "Rakoff": "Judge Rakoff",
    "Wigdor": "Wigdor LLP",
}

# Skip these — too generic or not real person names
SKIP = {
    "", "EFTA", "REDACTED", "FBI", "SDNY", "DOJ", "OPR", "DANY",
    "United States", "New York", "Palm Beach", "Virgin Islands",
    "Manhattan", "Paris", "Las Vegas", "New Mexico", "Florida",
    "Apollo", "Deutsche Bank", "JP Morgan", "Bear Stearns",
    "Victoria", "Secret", "Victoria's Secret",
    "SHU", "MCC", "NPA", "USVI", "NYC", "LLC", "Inc",
    "Southern Trust", "Financial Trust", "Hyperion Air", "JEGE",
    "Karin Models", "L Brands",
}


# ---------------------------------------------------------------------------
# EFTA page mapping from OCR markers
# ---------------------------------------------------------------------------

def build_page_map(content):
    """Build a mapping: character position → EFTA page number.

    OCR markers are footers: marker N appears AFTER page N's text.
    So text between marker (N-1) and marker N belongs to page N.
    Returns list of (start_pos, end_pos, efta_page_num).
    """
    marker_re = re.compile(r"EFTA(\d{5,8})")
    markers = [(m.start(), int(m.group(1))) for m in marker_re.finditer(content)]

    pages = []
    for i, (pos, num) in enumerate(markers):
        # Text after this marker until the next marker belongs to page (num+1)
        start = pos
        if i + 1 < len(markers):
            end = markers[i + 1][0]
        else:
            end = len(content)
        pages.append((start, end, num + 1))

    return pages


def pos_to_efta(char_pos, page_map):
    """Find which EFTA page a character position falls on."""
    for start, end, efta in page_map:
        if start <= char_pos < end:
            return efta
    return None


# ---------------------------------------------------------------------------
# Name normalization
# ---------------------------------------------------------------------------

def normalize_name(name):
    """Normalize a person name to canonical form."""
    name = name.strip()
    # Remove leading/trailing punctuation
    name = re.sub(r'^[\W_]+|[\W_]+$', '', name)
    if not name or len(name) < 2:
        return None

    # Skip known non-persons
    if name in SKIP or name.upper() in SKIP:
        return None

    # Skip all-caps short strings (likely OCR noise)
    if name.isupper() and len(name) < 5:
        return None

    # Check aliases
    if name in ALIASES:
        return ALIASES[name]

    # Check if any alias key is a substring match for multi-word names
    # e.g. "Leon Black" contains "Black" but we prefer exact match first
    for alias, canonical in ALIASES.items():
        if name == alias:
            return canonical

    # Skip single common words that spaCy misidentifies
    if len(name.split()) == 1 and name.lower() in {
        "said", "also", "told", "would", "asked", "went", "gave",
        "took", "made", "left", "came", "began", "continued",
        "mr", "ms", "mrs", "dr", "hon", "agent", "detective",
    }:
        return None

    return name


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract():
    print("Loading SpaCy model (en_core_web_lg)...")
    nlp = spacy.load("en_core_web_lg")
    # Increase max length for large files
    nlp.max_length = 2_000_000

    ocr_files = sorted(
        f for f in os.listdir(OCR_DIR)
        if f.startswith("epstein_ren") and f.endswith(".txt")
    )
    print(f"Found {len(ocr_files)} OCR files.\n")

    # Master data structures
    entities = defaultdict(lambda: {"count": 0, "occurrences": []})
    page_names = defaultdict(set)  # efta_page → set of names on that page
    keyword_hits = defaultdict(lambda: defaultdict(int))  # name → keyword → count

    keyword_pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in KEYWORDS) + r')\b',
        re.IGNORECASE,
    )

    for file_idx, ocr_file in enumerate(ocr_files):
        filepath = os.path.join(OCR_DIR, ocr_file)
        print(f"[{file_idx+1}/{len(ocr_files)}] Processing {ocr_file}...")

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        page_map = build_page_map(content)
        lines = content.split("\n")

        # Build line offset map for line numbers
        line_offsets = []
        offset = 0
        for line in lines:
            line_offsets.append(offset)
            offset += len(line) + 1

        # Process in chunks to manage memory
        chunk_size = 500_000
        for chunk_start in range(0, len(content), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(content))
            # Extend to next newline to avoid splitting mid-sentence
            while chunk_end < len(content) and content[chunk_end] != '\n':
                chunk_end += 1
            chunk = content[chunk_start:chunk_end]

            doc = nlp(chunk)

            for ent in doc.ents:
                if ent.label_ != "PERSON":
                    continue

                name = normalize_name(ent.text)
                if not name:
                    continue

                # Absolute position in file
                abs_pos = chunk_start + ent.start_char
                efta_page = pos_to_efta(abs_pos, page_map)

                # Find line number
                line_num = 1
                for i, lo in enumerate(line_offsets):
                    if lo > abs_pos:
                        break
                    line_num = i + 1

                # Context: 50 words around the entity
                ctx_start = max(0, abs_pos - 200)
                ctx_end = min(len(content), abs_pos + len(ent.text) + 200)
                context_raw = content[ctx_start:ctx_end].replace("\n", " ")
                # Trim to ~50 words
                words = context_raw.split()
                if len(words) > 50:
                    # Center around the entity
                    mid = len(words) // 2
                    start_w = max(0, mid - 25)
                    words = words[start_w:start_w + 50]
                context = " ".join(words)

                entities[name]["count"] += 1
                entities[name]["occurrences"].append({
                    "file": ocr_file,
                    "line": line_num,
                    "efta_page": efta_page,
                    "context": context,
                })

                if efta_page:
                    page_names[efta_page].add(name)

                # Keyword proximity check (within the context window)
                for kw_match in keyword_pattern.finditer(context.lower()):
                    keyword_hits[name][kw_match.group().lower()] += 1

        print(f"  → {len(entities)} unique names so far")

    # ---------------------------------------------------------------------------
    # Build outputs
    # ---------------------------------------------------------------------------

    print(f"\nTotal unique names: {len(entities)}")

    # 1. entities.json
    entities_out = {}
    for name, data in sorted(entities.items(), key=lambda x: -x[1]["count"]):
        entities_out[name] = {
            "count": data["count"],
            "occurrences": data["occurrences"],
        }

    out_path = os.path.join(OUT_DIR, "entities.json")
    with open(out_path, "w") as f:
        json.dump(entities_out, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path} ({len(entities_out)} names)")

    # 2. cooccurrence.json
    cooccurrence = defaultdict(lambda: {"count": 0, "pages": []})
    for efta_page, names in page_names.items():
        names_list = sorted(names)
        for i in range(len(names_list)):
            for j in range(i + 1, len(names_list)):
                key = f"{names_list[i]}||{names_list[j]}"
                cooccurrence[key]["count"] += 1
                cooccurrence[key]["pages"].append(efta_page)

    cooc_out = {}
    for key, data in sorted(cooccurrence.items(), key=lambda x: -x[1]["count"]):
        parts = key.split("||", 1)
        if len(parts) != 2:
            continue
        a, b = parts
        cooc_out[key] = {
            "name_a": a,
            "name_b": b,
            "count": data["count"],
            "pages": sorted(data["pages"]),
        }

    out_path = os.path.join(OUT_DIR, "cooccurrence.json")
    with open(out_path, "w") as f:
        json.dump(cooc_out, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path} ({len(cooc_out)} pairs)")

    # 3. flagged.json — names scored by keyword proximity
    flagged = []
    for name, kw_dict in keyword_hits.items():
        total_score = sum(kw_dict.values())
        flagged.append({
            "name": name,
            "total_score": total_score,
            "keyword_breakdown": dict(kw_dict),
            "occurrence_count": entities[name]["count"],
        })
    flagged.sort(key=lambda x: -x["total_score"])

    out_path = os.path.join(OUT_DIR, "flagged.json")
    with open(out_path, "w") as f:
        json.dump(flagged, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path} ({len(flagged)} flagged names)")

    print("\nDone.")


if __name__ == "__main__":
    extract()
