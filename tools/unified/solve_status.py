#!/usr/bin/env python3
"""Print the solve status dashboard."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SM = os.path.join(REPO, "tools", "unified", "solve_map.json")

with open(SM) as f:
    sm = json.load(f)

G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"; B = "\033[1m"; X = "\033[0m"

print(f"\n{B}EPSTEIN FILES — SOLVE STATUS{X}")
print(f"{'═'*50}")

for cat_name in ["identity", "decision", "financial", "structural", "connection"]:
    cat = sm["categories"][cat_name]
    pct = cat["solved_percentage"]
    filled = pct // 10
    bar = '█' * filled + '░' * (10 - filled)
    color = G if pct >= 60 else Y if pct >= 30 else R
    label = cat_name.capitalize()
    print(f"  {label:<18} [{color}{bar}{X}] {pct:>3}%  ({cat['answered']}/{cat['total']} fully answered)")

print(f"{'═'*50}")
total = sm["total_questions"]
pct = sm["overall_percentage"]
filled = pct // 10
bar = '█' * filled + '░' * (10 - filled)
color = G if pct >= 60 else Y if pct >= 30 else R
print(f"  {B}OVERALL{X}           [{color}{bar}{X}] {pct:>3}%  ({sm['answered']}/{total} fully, {sm['partially_answered']} partial, {sm['unsolvable']} unsolvable)")

print(f"\n{B}TOP UNSOLVED (highest value × solvability):{X}")
for i, q in enumerate(sm.get("highest_value_unsolved", [])[:5], 1):
    cat = q.get("_category", "?").upper()
    print(f"  {i}. {q['question'][:65]}")
    print(f"     [{cat}] significance={q.get('significance','?')} solvability={q['solvability']}")
print()
