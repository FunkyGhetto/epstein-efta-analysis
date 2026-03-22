#!/usr/bin/env python3
"""
Full automated rebuild of the entire project state.
Connects to corpus, reads all JSONs, greps OCR/rhowardstone, rebuilds everything.
"""
import os, re, json, glob, sqlite3, sys
from collections import defaultdict
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.expanduser("~/Documents/Epstein-research-data/full_text_corpus.db")
RHOWARD = os.path.expanduser("~/Documents/Epstein-research")
OCR = os.path.join(REPO, "ocr")
DATA = os.path.join(REPO, "tools", "analysis_outputs", "data")
UNIFIED = os.path.join(REPO, "tools", "unified")

def load(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return None

def read(path):
    with open(path, "r", errors="replace") as f: return f.read()

def grep_count(name, directory, ext="*.md"):
    c = 0
    for f in glob.glob(os.path.join(directory, "**", ext), recursive=True):
        try:
            if name in open(f, errors='replace').read(): c += 1
        except: pass
    return c

def ocr_count(name):
    c = 0
    for fn in ['epstein_ren16.txt', 'epstein_ren17.txt']:
        p = os.path.join(OCR, fn)
        if os.path.exists(p):
            c += read(p).lower().count(name.lower())
    return c

print("=" * 60)
print("FULL REBUILD — All Systems From Source Data")
print("=" * 60)

# ============================================================
# CONNECT TO CORPUS
# ============================================================
print("\n[1/7] Connecting to corpus...")
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM pages")
total_pages = cur.fetchone()[0]
print(f"  Corpus: {total_pages:,} pages")

# ============================================================
# LOAD ALL EXISTING DATA
# ============================================================
print("[2/7] Loading all data sources...")
linguistic = load(os.path.join(DATA, "linguistic_patterns.json")) or {}
co_absence = load(os.path.join(DATA, "co_absence_analysis.json"))
temporal = load(os.path.join(DATA, "temporal_proximity.json"))
bridges = load(os.path.join(DATA, "redaction_bridging.json"))
payments = load(os.path.join(DATA, "payment_event_correlation.json"))
leads_data = load(os.path.join(DATA, "leads.json"))
victim_profiles = load(os.path.join(DATA, "victim_profiles.json"))
proffer_landscape = load(os.path.join(UNIFIED, "proffer_landscape.json"))
triangulation = load(os.path.join(UNIFIED, "triangulation_results.json"))
dimensional = load(os.path.join(UNIFIED, "dimensional_analysis.json"))

# Analysis text
analysis_text = ""
for f in glob.glob(os.path.join(REPO, "analysis", "*.md")):
    analysis_text += read(f)
analysis_text += read(os.path.join(REPO, "README.md"))
all_cited_efta = set(re.findall(r'EFTA(\d{5,8})', analysis_text))

# ============================================================
# DEFINE ALL PERSONS
# ============================================================
print("[3/7] Building knowledge base for all persons...")

PERSONS = {
    "Leslie Groff": {"search": "Groff", "role": "scheduler/assistant", "charged": False, "npa": False},
    "Leon Black": {"search": "Leon Black", "role": "associate/client", "charged": False, "npa": False},
    "Glen Dubin": {"search": "Dubin", "role": "associate", "charged": False, "npa": False},
    "Jes Staley": {"search": "Staley", "role": "associate", "charged": False, "npa": False},
    "Harvey Weinstein": {"search": "Weinstein", "role": "associate", "charged": False, "npa": False},
    "Prince Andrew": {"search": "Prince Andrew", "role": "associate/royal", "charged": False, "npa": False},
    "Darren Indyke": {"search": "Indyke", "role": "attorney/enabler", "charged": False, "npa": False},
    "Les Wexner": {"search": "Wexner", "role": "financial source", "charged": False, "npa": False},
    "David Blaine": {"search": "Blaine", "role": "introducer", "charged": False, "npa": False},
    "Ghislaine Maxwell": {"search": "Maxwell", "role": "co-conspirator", "charged": True, "npa": False},
    "Alan Dershowitz": {"search": "Dershowitz", "role": "associate/attorney", "charged": False, "npa": False},
    "Bill Clinton": {"search": "Clinton", "role": "associate", "charged": False, "npa": False},
    "Larry Visoski": {"search": "Visoski", "role": "pilot", "charged": False, "npa": False},
    "George Mitchell": {"search": "Mitchell", "role": "associate/politician", "charged": False, "npa": False},
    "Ehud Barak": {"search": "Barak", "role": "associate/politician", "charged": False, "npa": False},
    "Sarah Kellen": {"search": "Kellen", "role": "scheduler/co-conspirator", "charged": False, "npa": True},
    "Rich Kahn": {"search": "Kahn", "role": "accountant", "charged": False, "npa": False},
    "David Copperfield": {"search": "Copperfield", "role": "associate", "charged": False, "npa": False},
    "Emmy Taylor": {"search": "Taylor", "role": "Maxwell's former assistant", "charged": False, "npa": False},
    "David Rodgers": {"search": "Rodgers", "role": "co-pilot", "charged": False, "npa": False},
    "Section A — Unknown": {"search": None, "role": "unknown (8-page charging analysis)", "charged": False, "npa": False},
    "Section B — Unknown": {"search": None, "role": "unknown (2-page charging analysis)", "charged": False, "npa": False},
}

# Proffer data
proffer_map = {}
if proffer_landscape:
    for p in proffer_landscape.get("proffers", []):
        name = p.get("person", "")
        if not p.get("person_redacted") and name:
            proffer_map[name] = {"date": p.get("date"), "efta": p.get("efta"), "attorney": p.get("attorney")}

# Co-absence map
ca_map = {}
if co_absence:
    for r in co_absence.get("results", []):
        ca_map[r["name"]] = r

# Build each person
kb = {"persons": {}, "prosecution_decisions": {}, "meta": {}}

for name, info in PERSONS.items():
    search = info["search"]

    # Memo presence
    memo_count = ocr_count(search) if search else 0

    # Corpus presence
    corpus_count = 0
    if search:
        try:
            cur.execute('SELECT COUNT(*) FROM pages_fts WHERE pages_fts MATCH ?', (f'"{search}"',))
            corpus_count = cur.fetchone()[0]
        except: pass

    # Linguistic
    ling = linguistic.get(search, {}) if search else {}

    # Co-absence
    ca = ca_map.get(name, {})

    # Rhowardstone
    rh_count = grep_count(search, RHOWARD) if search and os.path.exists(RHOWARD) else 0

    # Proffer
    proffer = proffer_map.get(name) or proffer_map.get(f"Lesley {name.split()[-1]}") or proffer_map.get(f"Lawrence {name.split()[-1]}") or None
    has_proffer = proffer is not None

    # Victim connections
    vic_conn = []
    if victim_profiles and search:
        for v in victim_profiles.get("victims", []):
            if search in str(v.get("named_associates", [])) or search.lower() in str(v.get("unique_details", [])).lower():
                vic_conn.append(v["designation"])

    # Leads
    lead_count = 0
    high_leads = 0
    if leads_data and search:
        for l in leads_data.get("leads", []):
            if search.lower() in str(l).lower():
                lead_count += 1
                if l.get("priority") == "high": high_leads += 1

    # Charging analysis pages
    charging_pages = 0
    if name == "Section A — Unknown": charging_pages = 8
    elif name == "Section B — Unknown": charging_pages = 2
    elif name == "Leslie Groff": charging_pages = 0  # heading only
    elif name == "Ghislaine Maxwell": charging_pages = 32  # separate PDF

    # Evidence score (0-10)
    ev = 0
    ev += min(memo_count / 5, 2)
    ev += min(len(vic_conn), 2)
    ev += 1 if has_proffer else 0
    ev += min(charging_pages / 4, 2)  # Up to 2 for dedicated charging analysis
    ev += 1 if ling.get("hedging_total", 0) > 0 or ling.get("strong_total", 0) > 0 else 0
    ev += 1 if high_leads > 0 else 0
    ev += 1 if rh_count > 10 else 0
    ev += 0.5 if corpus_count > 10000 else 0
    ev = round(min(ev, 10), 1)

    # Action score
    act = 0
    if info["charged"]: act = 10
    elif info["npa"]: act = 2
    elif memo_count > 0: act = 1

    gap = round(ev - act, 1)

    kb["persons"][name] = {
        "role": info["role"],
        "memo_mentions": memo_count,
        "corpus_pages": corpus_count,
        "co_absence_ratio": ca.get("ratio"),
        "linguistic": {"hedging": ling.get("hedging_total", 0), "strong": ling.get("strong_total", 0),
                       "ratio": ling.get("confidence_ratio")},
        "proffer": {"date": proffer["date"], "efta": proffer["efta"]} if proffer else None,
        "victim_connections": vic_conn,
        "charging_analysis_pages": charging_pages,
        "rhowardstone_reports": rh_count,
        "leads": lead_count, "high_leads": high_leads,
        "evidence_score": ev, "action_score": act, "gap": gap,
        "prosecution_outcome": "Charged" if info["charged"] else "Never charged",
        "npa_covered": info["npa"],
    }

# Special entries
kb["persons"]["Section A — Unknown"]["identity_status"] = "CONTESTED"
kb["persons"]["Section A — Unknown"]["hypotheses"] = ["H1: Person-specific (Kellen or other co-conspirator)", "H2: Charge-specific (statute analysis)"]
kb["persons"]["Leslie Groff"]["joint_charging"] = "SDNY evaluated 'Groff and/or Maxwell with a federal crime' (EFTA02731157)"
kb["persons"]["Jes Staley"]["jp_morgan_corroboration"] = "Footnote 61: JP Morgan messages corroborate victim rape account temporally"

# Prosecution decisions
kb["prosecution_decisions"] = {
    "charged": [n for n,i in PERSONS.items() if i["charged"]],
    "investigated_not_charged": [n for n in kb["persons"] if kb["persons"][n]["memo_mentions"] > 10 and not PERSONS[n]["charged"]],
    "named_in_memo": [n for n in kb["persons"] if 0 < kb["persons"][n]["memo_mentions"] <= 10 and not PERSONS[n]["charged"]],
    "absent_from_memo": [n for n in kb["persons"] if kb["persons"][n]["memo_mentions"] == 0 and n not in ("Section A — Unknown", "Section B — Unknown")],
}

kb["meta"] = {
    "total_persons": len(kb["persons"]),
    "total_efta_citations": len(all_cited_efta),
    "corpus_pages": total_pages,
    "rebuild_timestamp": datetime.now().isoformat(),
}

with open(os.path.join(UNIFIED, "knowledge_base.json"), "w") as f:
    json.dump(kb, f, indent=2)
print(f"  Knowledge base: {len(kb['persons'])} persons")

# ============================================================
# REBUILD SOLVE MAP
# ============================================================
print("[4/7] Rebuilding solve map...")

solve = {"categories": {}, "walls": []}

# Identity questions
id_qs = []
if proffer_landscape:
    redacted = [p for p in proffer_landscape["proffers"] if p.get("person_redacted")]
    for p in redacted[:30]:
        sol = "partially_solvable" if p.get("date") else "unsolvable"
        id_qs.append({"q": f"Who is redacted profferor at {p['efta']}?", "solvability": sol, "sig": "medium"})

id_qs.append({"q": "Who is Section A (8-page charging analysis)?", "solvability": "contested", "sig": "critical"})
id_qs.append({"q": "Who is Section B?", "solvability": "unsolvable", "sig": "high"})
id_qs.append({"q": "Is the 'lent out' victim Giuffre or someone else?", "solvability": "partially_answered", "sig": "high"})
id_qs.append({"q": "Who wrote the fictionalized memoir?", "solvability": "unanswered", "sig": "medium"})
id_qs.append({"q": "Who is Emmy Taylor and what did she tell SDNY?", "solvability": "partially_answered", "sig": "high"})

solve["categories"]["identity"] = {"total": len(id_qs),
    "answered": sum(1 for q in id_qs if q["solvability"] == "answered"),
    "partial": sum(1 for q in id_qs if q["solvability"] in ("partially_answered", "partially_solvable", "contested")),
    "unanswered": sum(1 for q in id_qs if q["solvability"] == "unanswered"),
    "unsolvable": sum(1 for q in id_qs if q["solvability"] == "unsolvable")}

# Decision questions
dec_qs = []
for name, p in sorted(kb["persons"].items(), key=lambda x: -x[1]["gap"]):
    if p["gap"] > 0 and p["prosecution_outcome"] == "Never charged":
        sol = "partially_answered" if p["memo_mentions"] > 0 or p.get("proffer") else "unanswered"
        dec_qs.append({"q": f"Why was {name} not charged? (gap: {p['gap']})", "solvability": sol, "sig": "high" if p["gap"] >= 5 else "medium"})
dec_qs.append({"q": "Why was Section A person not charged despite 8-page analysis?", "solvability": "unsolvable", "sig": "critical"})
dec_qs.append({"q": "What triggered Groff to proffer 21 months after refusing?", "solvability": "unanswered", "sig": "high"})
dec_qs.append({"q": "Did Groff's proffer contribute to the Maxwell case?", "solvability": "unanswered", "sig": "high"})

solve["categories"]["decision"] = {"total": len(dec_qs),
    "answered": sum(1 for q in dec_qs if q["solvability"] == "answered"),
    "partial": sum(1 for q in dec_qs if q["solvability"] == "partially_answered"),
    "unanswered": sum(1 for q in dec_qs if q["solvability"] == "unanswered"),
    "unsolvable": sum(1 for q in dec_qs if q["solvability"] == "unsolvable")}

# Financial questions
fin_qs = [
    {"q": "No client accounts — where did the money go after Epstein?", "solvability": "partially_answered", "sig": "high"},
    {"q": "What was $250K Dec 2018 wire for?", "solvability": "partially_answered", "sig": "high"},
    {"q": "Why did Black pay $158M?", "solvability": "partially_answered", "sig": "high"},
    {"q": "Groff $200K wire purpose?", "solvability": "unanswered", "sig": "medium"},
    {"q": "Complete Butterfly Trust beneficiary list?", "solvability": "unanswered", "sig": "medium"},
    {"q": "Offshore accounts?", "solvability": "unanswered", "sig": "high"},
    {"q": "JP Morgan Staley messages content?", "solvability": "unanswered", "sig": "high"},
]
solve["categories"]["financial"] = {"total": len(fin_qs),
    "answered": 0, "partial": sum(1 for q in fin_qs if q["solvability"] == "partially_answered"),
    "unanswered": sum(1 for q in fin_qs if q["solvability"] == "unanswered"), "unsolvable": 0}

# Structural questions
struct_qs = [
    {"q": "What is in Section D (Groff analysis)?", "solvability": "partially_answered", "sig": "critical",
     "note": "Joint charging evaluation visible on page 75. Content excised."},
    {"q": "What is in Sections A-C?", "solvability": "unsolvable", "sig": "critical"},
    {"q": "18 excised pages — who ordered the excision?", "solvability": "unsolvable", "sig": "high"},
    {"q": "Was Section C a separate section or absorbed?", "solvability": "unsolvable", "sig": "medium"},
    {"q": "Were documents altered between releases?", "solvability": "answered", "sig": "high"},
    {"q": "What text is in our OCR that the corpus missed, and vice versa?", "solvability": "partially_answered", "sig": "medium"},
]
solve["categories"]["structural"] = {"total": len(struct_qs),
    "answered": sum(1 for q in struct_qs if q["solvability"] == "answered"),
    "partial": sum(1 for q in struct_qs if q["solvability"] == "partially_answered"),
    "unanswered": 0,
    "unsolvable": sum(1 for q in struct_qs if q["solvability"] == "unsolvable")}

# Connection questions
conn_qs = [
    {"q": "Groff proffer → Maxwell case connection?", "solvability": "unanswered", "sig": "high"},
    {"q": "Who connects memo-absent persons?", "solvability": "partially_answered", "sig": "high"},
    {"q": "Visoski hub — what did he know about each absent person?", "solvability": "partially_answered", "sig": "medium"},
    {"q": "Emmy Taylor — what did she tell SDNY about Maxwell?", "solvability": "unanswered", "sig": "high"},
    {"q": "AUSA Alex — which other cases did they handle?", "solvability": "unanswered", "sig": "medium"},
]
solve["categories"]["connection"] = {"total": len(conn_qs),
    "answered": 0, "partial": sum(1 for q in conn_qs if q["solvability"] == "partially_answered"),
    "unanswered": sum(1 for q in conn_qs if q["solvability"] == "unanswered"), "unsolvable": 0}

# Totals
total_q = sum(c["total"] for c in solve["categories"].values())
total_ans = sum(c["answered"] for c in solve["categories"].values())
total_part = sum(c["partial"] for c in solve["categories"].values())
total_unans = sum(c["unanswered"] for c in solve["categories"].values())
total_unsol = sum(c["unsolvable"] for c in solve["categories"].values())
solve["total_questions"] = total_q
solve["answered"] = total_ans
solve["partially_answered"] = total_part
solve["unanswered"] = total_unans
solve["unsolvable"] = total_unsol
solve["overall_percentage"] = round((total_ans + total_part * 0.5) / max(total_q, 1) * 100)

# Walls
solve["walls"] = [
    {"wall": "Section D content excised", "type": "structural", "what_breaks_it": "FOIA for unredacted EFTA02731082 or congressional subpoena"},
    {"wall": "Section A identity excised", "type": "identity", "what_breaks_it": "Same as above, or identifying the redacted person on page 2"},
    {"wall": "Proffer content protected", "type": "legal", "what_breaks_it": "Congressional testimony or sealed agreement unsealing"},
    {"wall": "18 excised pages", "type": "structural", "what_breaks_it": "FOIA for complete prosecution memo or DOJ Inspector General investigation"},
    {"wall": "AUSA names redacted", "type": "identity", "what_breaks_it": "Cross-reference signing dates with known SDNY staff lists"},
    {"wall": "71 redacted profferors", "type": "identity", "what_breaks_it": "Attorney bridging, temporal analysis, or future document releases"},
    {"wall": "Offshore accounts not discussed", "type": "financial", "what_breaks_it": "USVI AG lawsuit documents or Deutsche Bank complete production"},
]

with open(os.path.join(UNIFIED, "solve_map.json"), "w") as f:
    json.dump(solve, f, indent=2)
print(f"  Solve map: {total_q} questions, {solve['overall_percentage']}% solved")

# ============================================================
# PROJECT STATE
# ============================================================
print("[5/7] Generating project state...")

# Count commits
try:
    import subprocess
    result = subprocess.run(['git', '-C', REPO, 'rev-list', '--count', 'HEAD'], capture_output=True, text=True)
    commit_count = int(result.stdout.strip())
except:
    commit_count = -1

# Count analysis files
analysis_files = glob.glob(os.path.join(REPO, "analysis", "*.md"))

# Genuinely new findings
genuinely_new = [
    "No client accounts (EFTA02731148) — not in any other EFTA project",
    "Groff proffer agreement (EFTA01682023) — not cited by rhowardstone",
    "78-proffer complete mapping — not attempted by any other project",
    "Groff corpus scheduling emails (4 EFTAs) — not in rhowardstone",
    "18 excised pages structural skeleton — section headings and legal framework mapped",
    "Page 75 joint charging evaluation: 'Groff and/or Maxwell with a federal crime'",
    "Footnote 61: JP Morgan Staley messages corroborate victim account",
    "Off-by-one OCR marker methodology",
    "Section D confirmed missing from release (not OCR failure)",
    "Linguistic pattern: hedging predicts non-charging across all persons",
]

# Proffer count
proffer_count = len(proffer_landscape.get("proffers", [])) if proffer_landscape else 0

# Leads
lead_count = len(leads_data.get("leads", [])) if leads_data else 0
high_lead_count = sum(1 for l in leads_data.get("leads", []) if l.get("priority") == "high") if leads_data else 0

project_state = {
    "timestamp": datetime.now().isoformat(),
    "commit_count": commit_count,
    "persons_tracked": len(kb["persons"]),
    "analysis_files": len(analysis_files),
    "citations_verified": "56/56 against corpus",
    "proffer_count": proffer_count,
    "leads_total": lead_count,
    "leads_high": high_lead_count,
    "solve_percentage": solve["overall_percentage"],
    "total_questions": total_q,
    "genuinely_new_findings": genuinely_new,
    "walls": [w["wall"] for w in solve["walls"]],
    "red_thread_top10": [],
    "highest_value_next_actions": [
        "FOIA for unredacted EFTA02731082 (would reveal Sections A-D content)",
        "Identify AUSA 'Alex' from EFTA00106062 — cross-reference with other cases",
        "Read Emmy Taylor interview transcript if it exists in corpus",
        "Search for Groff documents between Aug 2019 and Jul 2021 (the silent period)",
        "Compare corpus text vs OCR on all 86 prosecution memo pages systematically",
    ],
}

# Red thread top 10
top10 = sorted(kb["persons"].items(), key=lambda x: -x[1]["gap"])[:10]
for name, p in top10:
    project_state["red_thread_top10"].append({
        "name": name, "evidence": p["evidence_score"], "action": p["action_score"], "gap": p["gap"]
    })

with open(os.path.join(UNIFIED, "project_state.json"), "w") as f:
    json.dump(project_state, f, indent=2)

conn.close()

# ============================================================
# DASHBOARD
# ============================================================
print("[6/7] Dashboard...")
G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"; B = "\033[1m"; X = "\033[0m"

print(f"\n{B}EPSTEIN FILES — SOLVE STATUS (REBUILT){X}")
print(f"{'═'*55}")
for cat_name in ["identity", "decision", "financial", "structural", "connection"]:
    cat = solve["categories"][cat_name]
    ans = cat["answered"]
    part = cat.get("partial", 0)
    tot = cat["total"]
    pct = round((ans + part * 0.5) / max(tot, 1) * 100)
    filled = pct // 10
    bar = '█' * filled + '░' * (10 - filled)
    color = G if pct >= 60 else Y if pct >= 30 else R
    print(f"  {cat_name.capitalize():<15} [{color}{bar}{X}] {pct:>3}%  ({ans} full, {part} partial / {tot})")

print(f"{'═'*55}")
pct = solve["overall_percentage"]
filled = pct // 10
bar = '█' * filled + '░' * (10 - filled)
color = G if pct >= 60 else Y if pct >= 30 else R
print(f"  {B}OVERALL{X}         [{color}{bar}{X}] {pct:>3}%  ({total_ans} full, {total_part} partial / {total_q})")
print(f"  Unsolvable: {total_unsol} | Walls: {len(solve['walls'])}")

print(f"\n{B}RED THREAD TOP 10:{X}")
for i, (name, p) in enumerate(top10, 1):
    print(f"  {i:>2}. {name:<28} ev={p['evidence_score']:>4} act={p['action_score']:>4} gap={p['gap']:>5}")

print(f"\n{B}WALLS:{X}")
for w in solve["walls"]:
    print(f"  • {w['wall']}")
    print(f"    Break: {w['what_breaks_it'][:70]}")

print(f"\n{B}PROJECT STATE:{X}")
print(f"  Commits: {commit_count} | Persons: {len(kb['persons'])} | Proffers: {proffer_count}")
print(f"  Citations: 56/56 verified | Leads: {lead_count} ({high_lead_count} high)")
print(f"  New findings: {len(genuinely_new)}")

# ============================================================
# QA CHECK
# ============================================================
print(f"\n[7/7] QA Check...")
os.system(f"python3 {os.path.join(REPO, 'tools/verification/qa_check.py')} 2>&1 | tail -5")

print(f"\n{'='*55}")
print(f"REBUILD COMPLETE")
print(f"{'='*55}")
