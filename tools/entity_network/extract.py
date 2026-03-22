#!/usr/bin/env python3
"""
Entity extraction from EFTA OCR files using SpaCy NER.
Produces entities.json, cooccurrence.json, and flagged.json.

Filters applied:
  1. Only names within 1000 chars of an EFTA marker (excludes book content)
  2. OCR artifact removal (short, lowercase, fragment patterns)
  3. Repeated header/footer removal
  4. Legal citation removal (names after "v." / "vs.")
  5. Aggressive alias deduplication with auto-merge pass
  6. Textbook/non-document name blacklist

Usage: python3 extract.py
"""

import json
import os
import re
import sys
from collections import defaultdict, Counter

import spacy

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OCR_DIR = os.path.expanduser("~/Documents/epstein-efta-analysis/ocr/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Max distance (chars) from nearest EFTA marker to count a name
EFTA_PROXIMITY = 1000

KEYWORDS = [
    "massage", "minor", "underage", "recruit", "payment", "wire",
    "rape", "raped", "lent out", "sexual", "abuse",
]

# ---------------------------------------------------------------------------
# Alias map: variant → canonical
# ---------------------------------------------------------------------------

ALIASES = {
    # Epstein
    "Epstein": "Jeffrey Epstein",
    "Jeff Epstein": "Jeffrey Epstein",
    "EPSTEIN": "Jeffrey Epstein",
    "Jeffrey": "Jeffrey Epstein",
    "Jeffrey Epstein's": "Jeffrey Epstein",
    "A. Epstein": "Jeffrey Epstein",
    # Maxwell
    "Maxwell": "Ghislaine Maxwell",
    "MAXWELL": "Ghislaine Maxwell",
    "A. Maxwell's": "Ghislaine Maxwell",
    "b. MAXWELL": "Ghislaine Maxwell",
    "Maxwe": "Ghislaine Maxwell",
    "Maxwell's": "Ghislaine Maxwell",
    # Black
    "Black": "Leon Black",
    "Leon": "Leon Black",
    "LEON BLACK": "Leon Black",
    # Groff
    "Groff": "Leslie Groff",
    "Lesley Groff": "Leslie Groff",
    "GROFF": "Leslie Groff",
    # Indyke
    "Indyke": "Darren Indyke",
    # Wexner
    "Wexner": "Les Wexner",
    "Leslie Wexner": "Les Wexner",
    "WEXNER": "Les Wexner",
    # Acosta
    "Acosta": "Alexander Acosta",
    "R. Alexander Acosta": "Alexander Acosta",
    # Staley
    "Staley": "Jes Staley",
    # Brunel
    "Brunel": "Jean-Luc Brunel",
    "Jean Luc Brunel": "Jean-Luc Brunel",
    # Dubin
    "Dubin": "Glen Dubin",
    "Glen": "Glen Dubin",
    "Eva Dubin": "Glen Dubin",
    "Glen and Eva Dubin": "Glen Dubin",
    # Clinton
    "Clinton": "Bill Clinton",
    # Andrew
    "Prince Andrew": "Prince Andrew",
    "Andrew": "Prince Andrew",
    # Dershowitz
    "Dershowitz": "Alan Dershowitz",
    # Blaine
    "David Blane": "David Blaine",
    "Blaine": "David Blaine",
    "Blane": "David Blaine",
    "Blau": "David Blaine",
    # Copperfield
    "Copperfield": "David Copperfield",
    # Christensen
    "Christensen": "Jeanne Christensen",
    "Jeanne": "Jeanne Christensen",
    "Jeanne M. Christensen": "Jeanne Christensen",
    "Jeanne M Christensen": "Jeanne Christensen",
    # Others
    "Kahn": "Rich Kahn",
    "Rodriguez": "Michelle Rodriguez",
    "Marcinkova": "Nadia Marcinkova",
    "Kellen": "Sarah Kellen",
    "Alvarez": "Joseph Alvarez",
    "Klein": "Bella Klein",
    "Galindo": "Kimberly Galindo",
    "Noel": "Tova Noel",
    "Thomas": "Michael Thomas",
    "Harris": "Shahada Harris",
    "Edwards": "Brad Edwards",
    "Estrich": "Susan Estrich",
    "Rakoff": "Judge Rakoff",
    "Wigdor": "Wigdor LLP",
    # Maxwell variants
    "a. MAXWELL": "Ghislaine Maxwell",
    "A. MAXWELL": "Ghislaine Maxwell",
    # Epstein variants
    "A. Epstein's": "Jeffrey Epstein",
    # Weinstein
    "Weinstein": "Harvey Weinstein",
}

# Names to always skip — not real persons or from textbook/noise
SKIP = {
    # Organizations and places
    "", "EFTA", "REDACTED", "FBI", "SDNY", "DOJ", "OPR", "DANY",
    "United States", "New York", "Palm Beach", "Virgin Islands",
    "Manhattan", "Paris", "Las Vegas", "New Mexico", "Florida",
    "Apollo", "Deutsche Bank", "JP Morgan", "Bear Stearns",
    "Victoria", "Secret", "Victoria's Secret",
    "SHU", "MCC", "NPA", "USVI", "NYC", "LLC", "Inc",
    "Southern Trust", "Financial Trust", "Hyperion Air", "JEGE",
    "Karin Models", "L Brands",
    # Repeated headers/footers/legal boilerplate
    "R. CRIM", "FED", "Court Reporting", "FREE STATE REPORTING",
    "FREE STATE", "P.O. Box", "White Pis", "White Pls",
    "ATTORNEY WORK PRODUCT", "DELIBERATIVE PROCESS",
    # Textbook / massage book names
    "Bob Hope", "Mary Poppins", "Freud", "Sigmund Freud",
    "Michelangelo", "Henrik Ling", "Ida Rolf", "Steve Capellini",
    "Abel", "Vimala Schneider McClure", "Robin Leach",
    "Yaek Santitham", "Zeus", "James Bond", "Flopsy", "Peewee",
    "Hippocrates", "Galen", "Avicenna", "Paracelsus", "Ling",
    "Per Henrik Ling", "John Harvey Kellogg", "Dr. Kellogg",
    "Eunice Ingham", "Bonnie Prudden", "Janet Travell",
    # Common OCR-misidentified words
    "Doe", "Jane Doe", "John Doe",
    # Standalone words SpaCy misidentifies as persons
    "Minor", "Deep", "Wesley", "Brian", "Grace", "Luke",
    "Ashley", "Beck", "Hill", "Fodor", "Ingham",
    "Healthy Escapes", "Clare Maxwell Hudson",
}

# Patterns for OCR artifacts
OCR_FRAGMENT_RE = re.compile(
    r'^[a-z]{1,3}$'          # "ia", "iz", "ho", "mm"
    r'|^[A-Z]{1,2}$'         # "P", "A"
    r'|^[a-z]+\.$'           # "ii.", "stein."
    r'|^\d'                   # starts with digit
    r'|EFTA'
    r'|CRIM'
    r'|^[A-Z]\.\s'           # "A. ", "B. "
)


# ---------------------------------------------------------------------------
# EFTA page mapping
# ---------------------------------------------------------------------------

def build_marker_positions(content):
    """Return sorted list of (char_position, efta_number) for all markers."""
    return [(m.start(), int(m.group(1)))
            for m in re.finditer(r"EFTA(\d{5,8})", content)]


def build_page_map(markers):
    """Build page regions. Text between marker N and marker N+1 = page N+1."""
    pages = []
    for i, (pos, num) in enumerate(markers):
        start = pos
        end = markers[i + 1][0] if i + 1 < len(markers) else start + 10000
        pages.append((start, end, num + 1))
    return pages


def pos_to_efta(char_pos, page_map):
    """Find which EFTA page a character position falls on."""
    for start, end, efta in page_map:
        if start <= char_pos < end:
            return efta
    return None


def near_efta_marker(char_pos, markers, max_dist=EFTA_PROXIMITY):
    """Check if position is within max_dist chars of ANY EFTA marker."""
    # Binary search would be faster but markers list is small enough
    for mpos, _ in markers:
        if abs(char_pos - mpos) <= max_dist:
            return True
    return False


# ---------------------------------------------------------------------------
# Name normalization
# ---------------------------------------------------------------------------

def normalize_name(raw_name):
    """Normalize and filter a person name. Returns canonical name or None."""
    name = raw_name.strip()
    # Remove leading/trailing punctuation and whitespace
    name = re.sub(r'^[\W_]+|[\W_]+$', '', name)
    # Collapse internal whitespace/newlines
    name = re.sub(r'\s+', ' ', name).strip()

    if not name or len(name) <= 3:
        return None

    # All lowercase = OCR artifact
    if name.islower():
        return None

    # OCR fragment patterns
    if OCR_FRAGMENT_RE.match(name):
        return None

    # Skip list (case-sensitive first, then case-insensitive)
    if name in SKIP:
        return None
    if name.upper() in {s.upper() for s in SKIP}:
        return None

    # Possessive form → strip 's
    if name.endswith("'s"):
        name = name[:-2].strip()
        if not name or len(name) <= 3:
            return None

    # Check aliases (exact match)
    if name in ALIASES:
        return ALIASES[name]

    # Check aliases case-insensitive
    name_lower = name.lower()
    for alias, canonical in ALIASES.items():
        if name_lower == alias.lower():
            return canonical

    # Skip single common words that SpaCy misidentifies
    if len(name.split()) == 1 and name_lower in {
        "said", "also", "told", "would", "asked", "went", "gave",
        "took", "made", "left", "came", "began", "continued",
        "mr", "ms", "mrs", "dr", "hon", "agent", "detective",
        "judge", "counsel", "attorney", "victim", "subject",
        "stein", "jeff", "max", "black", "white", "brown",
        "grey", "gray", "green", "long", "young", "king",
        "ross", "lee", "grant", "west", "north", "south",
        "michel", "steve", "mike", "john", "david", "james",
        "mark", "paul", "peter", "george", "robert", "william",
        "sir", "lord", "duke", "baron", "count",
    }:
        return None

    # Names with newlines embedded = OCR noise
    if '\n' in name:
        return None

    return name


# ---------------------------------------------------------------------------
# Legal citation filter
# ---------------------------------------------------------------------------

def is_legal_citation(content, ent_start):
    """Check if the name appears right after 'v.' or 'vs.' (case citation)."""
    # Look at the 10 chars before the entity
    before = content[max(0, ent_start - 10):ent_start].strip()
    if re.search(r'\bv\.?\s*$', before) or re.search(r'\bvs\.?\s*$', before):
        return True
    return False


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract():
    print("Loading SpaCy model (en_core_web_lg)...")
    nlp = spacy.load("en_core_web_lg")
    nlp.max_length = 2_000_000

    ocr_files = sorted(
        f for f in os.listdir(OCR_DIR)
        if f.startswith("epstein_ren") and f.endswith(".txt")
    )
    print(f"Found {len(ocr_files)} OCR files.\n")

    # Pass 1: Collect raw entities
    raw_entities = defaultdict(lambda: {"count": 0, "occurrences": []})
    page_names = defaultdict(set)
    keyword_hits = defaultdict(lambda: defaultdict(int))

    # Track all text fragments to detect repeated headers
    text_line_counts = Counter()

    keyword_pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in KEYWORDS) + r')\b',
        re.IGNORECASE,
    )

    skipped_no_efta = 0
    skipped_artifact = 0
    skipped_citation = 0
    total_ents = 0

    for file_idx, ocr_file in enumerate(ocr_files):
        filepath = os.path.join(OCR_DIR, ocr_file)
        print(f"[{file_idx+1}/{len(ocr_files)}] Processing {ocr_file}...")

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        markers = build_marker_positions(content)
        page_map = build_page_map(markers)

        # Build line offset map
        line_offsets = []
        offset = 0
        for line in content.split("\n"):
            line_offsets.append(offset)
            offset += len(line) + 1

        # Count repeated lines for header detection
        for line in content.split("\n"):
            stripped = line.strip()
            if len(stripped) > 10:
                text_line_counts[stripped] += 1

        # Process in chunks
        chunk_size = 500_000
        for chunk_start in range(0, len(content), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(content))
            while chunk_end < len(content) and content[chunk_end] != '\n':
                chunk_end += 1
            chunk = content[chunk_start:chunk_end]

            doc = nlp(chunk)

            for ent in doc.ents:
                if ent.label_ != "PERSON":
                    continue
                total_ents += 1

                abs_pos = chunk_start + ent.start_char

                # FILTER 6: Only within EFTA_PROXIMITY of a marker
                if not near_efta_marker(abs_pos, markers):
                    skipped_no_efta += 1
                    continue

                # FILTER 4: Legal citation check
                if is_legal_citation(content, abs_pos):
                    skipped_citation += 1
                    continue

                # FILTER 2+3: Normalize (includes artifact and skip filtering)
                name = normalize_name(ent.text)
                if not name:
                    skipped_artifact += 1
                    continue

                efta_page = pos_to_efta(abs_pos, page_map)

                # Line number
                line_num = 1
                for i, lo in enumerate(line_offsets):
                    if lo > abs_pos:
                        break
                    line_num = i + 1

                # Context (~50 words)
                ctx_start = max(0, abs_pos - 200)
                ctx_end = min(len(content), abs_pos + len(ent.text) + 200)
                context_raw = content[ctx_start:ctx_end].replace("\n", " ")
                words = context_raw.split()
                if len(words) > 50:
                    mid = len(words) // 2
                    words = words[max(0, mid - 25):max(0, mid - 25) + 50]
                context = " ".join(words)

                raw_entities[name]["count"] += 1
                raw_entities[name]["occurrences"].append({
                    "file": ocr_file,
                    "line": line_num,
                    "efta_page": efta_page,
                    "context": context,
                })

                if efta_page:
                    page_names[efta_page].add(name)

                for kw_match in keyword_pattern.finditer(context.lower()):
                    keyword_hits[name][kw_match.group().lower()] += 1

        print(f"  → {len(raw_entities)} unique names so far")

    print(f"\nRaw PERSON entities found: {total_ents}")
    print(f"  Skipped (no EFTA nearby): {skipped_no_efta}")
    print(f"  Skipped (artifact/skip): {skipped_artifact}")
    print(f"  Skipped (legal citation): {skipped_citation}")
    print(f"  Kept: {total_ents - skipped_no_efta - skipped_artifact - skipped_citation}")

    # -----------------------------------------------------------------------
    # FILTER 3 (post-pass): Remove names that are repeated header/footer text
    # -----------------------------------------------------------------------
    repeated_lines = {line for line, count in text_line_counts.items() if count > 20}
    header_names = set()
    for name in list(raw_entities.keys()):
        for rl in repeated_lines:
            if name in rl:
                header_names.add(name)
                break

    for name in header_names:
        if name in raw_entities:
            del raw_entities[name]
    print(f"\nRemoved {len(header_names)} header/footer names")

    # -----------------------------------------------------------------------
    # FILTER 5 (post-pass): Auto-merge short names into full names
    # -----------------------------------------------------------------------
    # If a single-word name co-occurs on 60%+ of its pages with a multi-word
    # name that contains it, merge the short name into the longer one.
    name_pages = defaultdict(set)
    for efta_page, names in page_names.items():
        for n in names:
            if n in raw_entities:
                name_pages[n].add(efta_page)

    auto_merges = {}
    single_word_names = [n for n in raw_entities if len(n.split()) == 1 and n not in ALIASES.values()]
    multi_word_names = [n for n in raw_entities if len(n.split()) > 1]

    for short in single_word_names:
        short_pages = name_pages.get(short, set())
        if len(short_pages) < 3:
            continue
        best_match = None
        best_overlap = 0
        for full in multi_word_names:
            if short.lower() in full.lower() and short != full:
                full_pages = name_pages.get(full, set())
                overlap = len(short_pages & full_pages)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = full
        if best_match and best_overlap / len(short_pages) >= 0.6:
            auto_merges[short] = best_match

    # Apply auto-merges
    for short, full in auto_merges.items():
        if short in raw_entities and full in raw_entities:
            raw_entities[full]["count"] += raw_entities[short]["count"]
            raw_entities[full]["occurrences"].extend(raw_entities[short]["occurrences"])
            # Merge page_names
            for efta_page in list(page_names.keys()):
                if short in page_names[efta_page]:
                    page_names[efta_page].discard(short)
                    page_names[efta_page].add(full)
            # Merge keyword_hits
            if short in keyword_hits:
                for kw, cnt in keyword_hits[short].items():
                    keyword_hits[full][kw] += cnt
                del keyword_hits[short]
            del raw_entities[short]

    print(f"Auto-merged {len(auto_merges)} short names into full names")
    if auto_merges:
        for short, full in sorted(auto_merges.items()):
            print(f"  {short} → {full}")

    # -----------------------------------------------------------------------
    # Filter: Remove names with only 1 occurrence (noise)
    # -----------------------------------------------------------------------
    single_occ = [n for n, d in raw_entities.items() if d["count"] <= 1]
    for n in single_occ:
        del raw_entities[n]
    print(f"Removed {len(single_occ)} names with only 1 occurrence")

    entities = raw_entities
    print(f"\nFinal unique names: {len(entities)}")

    # -----------------------------------------------------------------------
    # Build outputs
    # -----------------------------------------------------------------------

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
        names_in_entities = sorted(n for n in names if n in entities)
        for i in range(len(names_in_entities)):
            for j in range(i + 1, len(names_in_entities)):
                key = f"{names_in_entities[i]}||{names_in_entities[j]}"
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

    # 3. flagged.json
    flagged = []
    for name, kw_dict in keyword_hits.items():
        if name not in entities:
            continue
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

    # Print top 30
    print("\n" + "=" * 80)
    print("TOP 30 FLAGGED NAMES")
    print("=" * 80)
    for entry in flagged[:30]:
        kws = ", ".join(f"{k}:{v}" for k, v in sorted(
            entry["keyword_breakdown"].items(), key=lambda x: -x[1])[:5])
        print(f"  {entry['name']:<30} score={entry['total_score']:<6} "
              f"occ={entry['occurrence_count']:<5} {kws}")

    print("\nDone.")


if __name__ == "__main__":
    extract()
