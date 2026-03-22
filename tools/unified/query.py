#!/usr/bin/env python3
"""
Query the unified knowledge base.

Usage:
  python3 query.py --person "Leslie Groff"
  python3 query.py --compare "Leslie Groff" "Sarah Kellen"
  python3 query.py --pattern hedging
  python3 query.py --absent
  python3 query.py --uncharged
  python3 query.py --connections "Leslie Groff"
  python3 query.py --red-thread
"""

import json
import sys
import os
import argparse

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KB_PATH = os.path.join(REPO, "tools", "unified", "knowledge_base.json")

def load_kb():
    with open(KB_PATH) as f:
        return json.load(f)

def print_person(name, p):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"  Role: {p['role']} | Outcome: {p['prosecution_outcome']}")
    print(f"{'='*60}")
    print(f"  Memo mentions: {p['memo_presence']['total_mentions']}")
    print(f"  Corpus pages:  {p['corpus_presence']['total_pages']:,}")
    print(f"  Co-absence ratio: {p['co_absence_ratio'] or 'N/A'}")
    print(f"  Evidence score: {p['evidence_score']}/10")
    print(f"  Action score:   {p['action_score']}/10")
    print(f"  GAP:            {p['gap']}")
    ling = p['linguistic_profile']
    print(f"  Linguistic: hedging={ling['hedging_count']} strong={ling['strong_count']} ratio={ling['ratio'] or 'N/A'}")
    print(f"  Financial connections: {p['financial_connections']}")
    print(f"  Victim connections: {len(p['victim_connections'])}")
    print(f"  Temporal events: {p['temporal_events']}")
    print(f"  Redaction bridges: {p['redaction_bridges']}")
    print(f"  Open leads: {p['open_leads']} (high: {p['high_leads']})")
    print(f"  Rhowardstone reports: {p['rhowardstone_reports']}")
    if p['comparable_person']:
        print(f"  Comparable: {p['comparable_person']}")
    if p['npa_covered']:
        print(f"  NPA: COVERED")
    if p['victim_connections']:
        print(f"  Victims:")
        for v in p['victim_connections'][:5]:
            print(f"    - {v['victim']}: {v['role']}")

def cmd_person(kb, name):
    if name in kb['persons']:
        print_person(name, kb['persons'][name])
    else:
        matches = [n for n in kb['persons'] if name.lower() in n.lower()]
        if matches:
            for m in matches:
                print_person(m, kb['persons'][m])
        else:
            print(f"Not found: {name}")

def cmd_compare(kb, name1, name2):
    p1 = kb['persons'].get(name1)
    p2 = kb['persons'].get(name2)
    if not p1 or not p2:
        print(f"Not found: {name1 if not p1 else name2}")
        return

    print(f"\n{'='*60}")
    print(f"  COMPARISON: {name1} vs {name2}")
    print(f"{'='*60}")
    fields = [
        ("Role", "role"),
        ("Outcome", "prosecution_outcome"),
        ("NPA covered", "npa_covered"),
        ("Memo mentions", lambda p: p['memo_presence']['total_mentions']),
        ("Corpus pages", lambda p: f"{p['corpus_presence']['total_pages']:,}"),
        ("Evidence score", "evidence_score"),
        ("Action score", "action_score"),
        ("GAP", "gap"),
        ("Hedging ratio", lambda p: p['linguistic_profile']['ratio'] or 'N/A'),
        ("Financial links", "financial_connections"),
        ("Victim links", lambda p: len(p['victim_connections'])),
        ("Open leads", "open_leads"),
    ]
    print(f"  {'Field':<25} {name1:<20} {name2:<20}")
    print(f"  {'-'*65}")
    for label, key in fields:
        if callable(key):
            v1, v2 = key(p1), key(p2)
        else:
            v1, v2 = p1.get(key, 'N/A'), p2.get(key, 'N/A')
        print(f"  {label:<25} {str(v1):<20} {str(v2):<20}")

def cmd_pattern(kb, pattern):
    if pattern == "hedging":
        people = [(n, p) for n, p in kb['persons'].items() if p['linguistic_profile']['ratio'] is not None]
        people.sort(key=lambda x: x[1]['linguistic_profile']['ratio'])
        print(f"\n  HEDGING PATTERN (low ratio = more hedging)")
        print(f"  {'Name':<25} {'Ratio':>8} {'Hedge':>6} {'Strong':>6} Outcome")
        print(f"  {'-'*70}")
        for n, p in people:
            ling = p['linguistic_profile']
            print(f"  {n:<25} {str(ling['ratio']):>8} {ling['hedging_count']:>6} {ling['strong_count']:>6} {p['prosecution_outcome']}")

def cmd_absent(kb):
    absent = [(n, p) for n, p in kb['persons'].items() if p['memo_presence']['total_mentions'] == 0]
    absent.sort(key=lambda x: x[1]['corpus_presence']['total_pages'], reverse=True)
    print(f"\n  ABSENT FROM PROSECUTION MEMO (sorted by corpus presence)")
    print(f"  {'Name':<25} {'Corpus pages':>12} {'Rhowardstone':>12} Role")
    print(f"  {'-'*70}")
    for n, p in absent:
        print(f"  {n:<25} {p['corpus_presence']['total_pages']:>12,} {p['rhowardstone_reports']:>12} {p['role']}")

def cmd_uncharged(kb):
    uncharged = [(n, p) for n, p in kb['persons'].items() if p['prosecution_outcome'] == 'Never charged' and p['evidence_score'] > 0]
    uncharged.sort(key=lambda x: x[1]['gap'], reverse=True)
    print(f"\n  UNCHARGED — sorted by gap (evidence - action)")
    print(f"  {'Name':<25} {'Evidence':>8} {'Action':>8} {'GAP':>8} {'Memo':>6} {'Corpus':>10} Role")
    print(f"  {'-'*85}")
    for n, p in uncharged:
        print(f"  {n:<25} {p['evidence_score']:>8} {p['action_score']:>8} {p['gap']:>8} {p['memo_presence']['total_mentions']:>6} {p['corpus_presence']['total_pages']:>10,} {p['role']}")

def cmd_connections(kb, name):
    p = kb['persons'].get(name)
    if not p:
        print(f"Not found: {name}")
        return
    print(f"\n  CONNECTIONS: {name}")
    print(f"  {'='*50}")
    if p['victim_connections']:
        print(f"\n  Victim connections:")
        for v in p['victim_connections']:
            print(f"    {v['victim']}: {v['role']}")
    print(f"\n  Financial: {p['financial_connections']} documented links")
    print(f"  Temporal: {p['temporal_events']} date matches")
    print(f"  Bridges: {p['redaction_bridges']} cross-document matches")
    print(f"  Open leads: {p['open_leads']} (high: {p['high_leads']})")

def cmd_red_thread(kb):
    people = [(n, p) for n, p in kb['persons'].items()]
    people.sort(key=lambda x: x[1]['gap'], reverse=True)

    print(f"\n{'='*80}")
    print(f"  THE RED THREAD: Evidence vs Prosecution Action")
    print(f"  Sorted by gap — largest gap = most significant discrepancy")
    print(f"{'='*80}")
    print(f"\n  {'#':>3} {'Name':<25} {'Evidence':>8} {'Action':>8} {'GAP':>6} {'Ling':>6} {'Outcome':<20}")
    print(f"  {'-'*85}")

    for i, (n, p) in enumerate(people, 1):
        ling_ratio = p['linguistic_profile']['ratio']
        ling_str = f"{ling_ratio:.2f}" if ling_ratio is not None else "N/A"
        print(f"  {i:>3} {n:<25} {p['evidence_score']:>8} {p['action_score']:>8} {p['gap']:>6} {ling_str:>6} {p['prosecution_outcome']:<20}")

    print(f"\n{'='*80}")
    print(f"  ANALYSIS")
    print(f"{'='*80}")

    # Top 5 gaps
    top = people[:5]
    print(f"\n  Top 5 evidence-action gaps:")
    for n, p in top:
        print(f"\n  {n} (gap: {p['gap']})")
        print(f"    Evidence: {p['evidence_score']}/10 | Action: {p['action_score']}/10")
        print(f"    Memo: {p['memo_presence']['total_mentions']} mentions | Corpus: {p['corpus_presence']['total_pages']:,} pages")
        ling = p['linguistic_profile']
        if ling['hedging_count'] or ling['strong_count']:
            print(f"    Linguistic: {ling['hedging_count']} hedging / {ling['strong_count']} strong (ratio {ling['ratio']})")
        if p['victim_connections']:
            print(f"    Victim connections: {len(p['victim_connections'])}")
        if p['comparable_person']:
            print(f"    Comparable: {p['comparable_person']}")

    print(f"\n  Key pattern: People the memo discusses at length with hedging language")
    print(f"  were never charged. People discussed with confident language were charged.")
    print(f"  The prosecution memo's linguistic choices predicted its own outcomes.")

def main():
    parser = argparse.ArgumentParser(description="Query the unified knowledge base")
    parser.add_argument("--person", help="Show everything about a person")
    parser.add_argument("--compare", nargs=2, help="Compare two people side by side")
    parser.add_argument("--pattern", help="Show pattern (e.g., 'hedging')")
    parser.add_argument("--absent", action="store_true", help="Show people absent from memo")
    parser.add_argument("--uncharged", action="store_true", help="Show uncharged people by evidence")
    parser.add_argument("--connections", help="Show connections for a person")
    parser.add_argument("--red-thread", action="store_true", help="The full narrative: evidence vs action")

    args = parser.parse_args()
    kb = load_kb()

    if args.person:
        cmd_person(kb, args.person)
    elif args.compare:
        cmd_compare(kb, args.compare[0], args.compare[1])
    elif args.pattern:
        cmd_pattern(kb, args.pattern)
    elif args.absent:
        cmd_absent(kb)
    elif args.uncharged:
        cmd_uncharged(kb)
    elif args.connections:
        cmd_connections(kb, args.connections)
    elif args.red_thread:
        cmd_red_thread(kb)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
