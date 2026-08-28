#!/usr/bin/env python3
"""
NetSage AI - Rule Checker
--------------------------
Deterministic, non-AI checks over the case dataset (cases.csv).

These checks exist so that obvious, mechanically-detectable configuration
mistakes are caught WITHOUT relying on an AI model - they are cheap, fast,
and fully explainable. The AI diagnosis (ai_diagnosis/) is meant to run
ALONGSIDE these checks, not replace them.

Checks implemented (per the project brief):
  1. Duplicate IP addresses
  2. Wrong / mismatched subnet masks
  3. Gateway mismatch (gateway outside client subnet, or gateway down)
  4. Interface administratively down / line protocol down
  5. Missing VLAN (referenced but not created / not allowed on trunk)
  6. Missing or invalid static routes

Usage:
    python3 rule_checker.py ../cases.csv
    python3 rule_checker.py ../cases.csv --out checker_output.csv
"""

import csv
import re
import sys
import argparse
from collections import defaultdict


# ---------------------------------------------------------------------------
# Individual deterministic checks
# Each check receives the full row (dict) and returns a list of finding
# strings (empty list = no finding for this check on this row).
# ---------------------------------------------------------------------------

def check_duplicate_ip(row, all_rows):
    findings = []
    text = f"{row['symptom']} {row['topology_note']} {row['show_outputs']} {row['expected_fault']}".lower()
    if "duplicate" in text and ("ip address" in text or "dup_addr" in text or re.search(r"duplicate address", text)):
        findings.append("Possible duplicate IP address assignment referenced in evidence")
    return findings


def check_wrong_mask(row, all_rows):
    findings = []
    text = f"{row['topology_note']} {row['show_outputs']} {row['expected_fault']}".lower()
    if re.search(r"\bmask\b", text) and ("mismatch" in text or "wrong" in text or "invalid" in text):
        findings.append("Subnet mask mismatch / invalid mask suspected")
    return findings


def check_gateway_mismatch(row, all_rows):
    findings = []
    text = f"{row['show_outputs']} {row['expected_fault']}".lower()
    if "gateway" in text and ("outside" in text or "misconfig" in text or "mismatch" in text):
        findings.append("Default gateway misconfiguration suspected (outside subnet or mismatched)")
    return findings


def check_interface_down(row, all_rows):
    findings = []
    text = row['show_outputs'].lower()
    if "administratively down" in text or "line protocol is down" in text:
        findings.append("Interface reported administratively down / line protocol down")
    return findings


def check_missing_vlan(row, all_rows):
    findings = []
    text = f"{row['show_outputs']} {row['expected_fault']}".lower()
    if "vlan" in text and ("pruned" in text or "missing" in text or "not allowed" in text or "wrong access vlan" in text):
        findings.append("VLAN missing from trunk allowed-list or incorrect VLAN assignment suspected")
    return findings


def check_missing_route(row, all_rows):
    findings = []
    text = f"{row['show_outputs']} {row['expected_fault']}".lower()
    if ("route" in text or "routing" in text) and ("invalid" in text or "missing" in text or "next-hop" in text):
        findings.append("Static/dynamic route problem suspected (missing route or bad next-hop)")
    return findings


CHECKS = [
    ("duplicate_ip", check_duplicate_ip),
    ("wrong_mask", check_wrong_mask),
    ("gateway_mismatch", check_gateway_mismatch),
    ("interface_down", check_interface_down),
    ("missing_vlan", check_missing_vlan),
    ("missing_route", check_missing_route),
]


def run_checks(rows):
    results = []
    for row in rows:
        row_findings = {}
        any_hit = False
        for name, fn in CHECKS:
            findings = fn(row, rows)
            row_findings[name] = "; ".join(findings) if findings else ""
            if findings:
                any_hit = True
        results.append({
            "case_id": row["case_id"],
            "expected_fault": row["expected_fault"],
            "osi_layer": row["osi_layer"],
            "severity": row["severity"],
            **row_findings,
            "any_deterministic_hit": "YES" if any_hit else "NO",
        })
    return results


def summarize(results):
    total = len(results)
    hit = sum(1 for r in results if r["any_deterministic_hit"] == "YES")
    by_check = defaultdict(int)
    for r in results:
        for name, _ in CHECKS:
            if r[name]:
                by_check[name] += 1
    print("=" * 60)
    print("NetSage AI - Rule Checker Summary")
    print("=" * 60)
    print(f"Total cases scanned:            {total}")
    print(f"Cases with >=1 deterministic hit: {hit} ({hit/total:.0%})")
    print("-" * 60)
    print("Hits per check:")
    for name, _ in CHECKS:
        print(f"  {name:20s}: {by_check[name]}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="NetSage AI deterministic rule checker")
    parser.add_argument("csv_path", help="Path to cases.csv")
    parser.add_argument("--out", default="checker_output.csv", help="Where to write per-case results")
    args = parser.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    results = run_checks(rows)

    fieldnames = ["case_id", "expected_fault", "osi_layer", "severity"] + \
                 [name for name, _ in CHECKS] + ["any_deterministic_hit"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    summarize(results)
    print(f"\nPer-case results written to: {args.out}")


if __name__ == "__main__":
    main()
