#!/usr/bin/env python3
"""
NetSage AI - Batch Diagnosis Runner
------------------------------------
Feeds every case in cases.csv through the diagnose_prompt.md prompt and
writes one JSON diagnosis per case, plus a comparison against the
human-labeled expected_fault so reviewers can see agree/disagree at a
glance.

This script is written to call the Anthropic Messages API. Set
ANTHROPIC_API_KEY in your environment before running it against a live
model. ai_responses.json in this folder is the saved output of a run
already performed for this submission (so the project can be graded
without needing an API key).

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python3 run_diagnosis.py ../cases.csv --prompt ../prompts/diagnose_prompt.md
"""

import csv
import json
import os
import re
import argparse

try:
    import anthropic
except ImportError:
    anthropic = None


SYSTEM_PROMPT = """You are NetSage AI, a network-troubleshooting assistant for Cisco-style
Packet Tracer labs. Base every claim ONLY on the given symptom, topology
note, and show-command output. Return ONLY valid JSON with keys:
case_id, root_cause, osi_layer, confidence (Low/Medium/High), evidence,
next_command, fix_steps (array of strings). No prose outside the JSON."""


def build_user_prompt(row):
    return (
        f"CASE ID: {row['case_id']}\n"
        f"SYMPTOM: {row['symptom']}\n"
        f"TOPOLOGY NOTE: {row['topology_note']}\n"
        f"SHOW-COMMAND OUTPUT: {row['show_outputs']}\n\n"
        "Diagnose this case following the OUTPUT SCHEMA exactly."
    )


def call_model(client, row):
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(row)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


def compare(ai_result, expected_fault):
    """Very rough keyword overlap check - a human still makes the real call."""
    ai_text = ai_result.get("root_cause", "").lower()
    expected_words = set(re.findall(r"[a-z0-9]+", expected_fault.lower()))
    ai_words = set(re.findall(r"[a-z0-9]+", ai_text))
    overlap = expected_words & ai_words
    if len(overlap) >= max(2, len(expected_words) // 2):
        return "likely_match"
    return "needs_human_review"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--prompt", default="../prompts/diagnose_prompt.md")
    parser.add_argument("--out", default="ai_responses_live.json")
    args = parser.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if anthropic is None or not os.environ.get("ANTHROPIC_API_KEY"):
        print("anthropic SDK not installed or ANTHROPIC_API_KEY not set.")
        print("Using saved ai_responses.json instead of calling a live model.")
        print("(See ai_diagnosis/ai_responses.json for the diagnosis already")
        print(" produced for this submission.)")
        return

    client = anthropic.Anthropic()
    results = []
    for row in rows:
        try:
            ai_result = call_model(client, row)
        except Exception as e:
            ai_result = {"case_id": row["case_id"], "error": str(e)}
        ai_result["_agreement_hint"] = compare(ai_result, row["expected_fault"])
        results.append(ai_result)
        print(f"{row['case_id']}: {ai_result.get('root_cause', ai_result.get('error'))}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {len(results)} diagnoses to {args.out}")


if __name__ == "__main__":
    main()
