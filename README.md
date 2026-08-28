# NetSage AI
**Project 2 | Applied AI + Network Troubleshooting**
*Build an AI troubleshooting helper with human review*

NetSage AI is a troubleshooting assistant for Cisco-style Packet Tracer
labs. It reads a symptom, a topology note, and show-command output, and
proposes a likely root cause, OSI layer, next command, and fix — but a
**human reviewer must Accept, Edit, or Reject every diagnosis** before any
fix is treated as final. Nothing here is applied automatically to a
device.

## Project structure

```
NetSage_AI/
├── README.md                          this file
├── cases.csv                          30 troubleshooting cases (given dataset)
├── prompts/
│   └── diagnose_prompt.md             system + user prompt, JSON schema, 3 worked examples,
│                                       batch-mode prompt, reviewer-assist prompt
├── checker/
│   ├── rule_checker.py                deterministic (non-AI) config-mistake checks
│   ├── checker_output.csv             per-case results of running the checker
│   └── sample_output.txt              console summary from a sample run
├── ai_diagnosis/
│   ├── run_diagnosis.py               batch runner that calls the Anthropic API
│   │                                   with diagnose_prompt.md against cases.csv
│   └── ai_responses.json              saved AI diagnosis for all 30 cases (JSON,
│                                       one object per case, matches the output schema)
├── human_review/
│   ├── review_log.csv                 case-by-case Accepted / Edited / Rejected verdicts
│   │                                   + reviewer notes, for all 30 cases
│   └── responsible_ai_log.md          detailed write-up of the 8 cases that needed
│                                       a human correction (>= 5 required)
├── dashboard/
│   └── NetSage_AI_Dashboard.xlsx      case data + summary counts (severity, OSI layer,
│                                       concept tag) + AI-vs-human agreement rate + charts
└── docs/
    └── demo_video_script.md           shot-by-shot script for the 5-10 min demo video
```

## How the pieces fit together (matches the project's step-by-step workflow)

1. **Collect real lab cases** → `cases.csv` — 30 cases spanning VLAN, gateway,
   DHCP, DNS, routing, ACL, NAT, wireless, IPv6, HSRP, VTP, port security,
   and CDP faults.
2. **Write structured prompts** → `prompts/diagnose_prompt.md` — forces JSON
   output (`root_cause`, `confidence`, `evidence`, `next_command`,
   `fix_steps`) and includes 3 worked examples.
3. **Build the rule checker** → `checker/rule_checker.py` — six deterministic
   checks (duplicate IP, wrong mask, gateway mismatch, interface down,
   missing VLAN, missing/invalid route) that run independently of the AI.
4. **Run AI diagnosis** → `ai_diagnosis/run_diagnosis.py` produces
   `ai_responses.json` by sending every case through the prompt above.
5. **Add human review** → `human_review/review_log.csv` marks every case
   Accepted / Edited / Rejected with reviewer notes;
   `human_review/responsible_ai_log.md` documents the 8 cases (7 Edited,
   1 Rejected) where the AI needed correction, including two clear
   hallucinations (NET-013, NET-024) that never should have reached a
   device unreviewed.
6. **Build the dashboard and demo** → `dashboard/NetSage_AI_Dashboard.xlsx`
   summarizes issue types, severity, OSI layer, and the AI-vs-human
   agreement rate (73%); `docs/demo_video_script.md` scripts the demo.

## Key results

| Metric | Value |
|---|---|
| Total cases | 30 |
| Accepted as-is | 22 (73%) |
| Edited by reviewer | 7 |
| Rejected by reviewer | 1 |
| Deterministic rule-checker hits | 8 of 30 cases (27%) |

## Reproducing the AI diagnosis run

```bash
export ANTHROPIC_API_KEY=sk-...
cd ai_diagnosis
python3 run_diagnosis.py ../cases.csv --prompt ../prompts/diagnose_prompt.md
```

If no API key is set, the script explains this and points to the saved
`ai_responses.json`, so the project can be graded without live API access.

## Reproducing the rule checker

```bash
cd checker
python3 rule_checker.py ../cases.csv --out checker_output.csv
```

## Safety rule

Per the problem statement, **a human reviewer must approve or correct
every diagnosis**. This project treats that as a hard requirement, not a
suggestion: no `fix_steps` from `ai_diagnosis/` are ever presented as
final until they carry an "Accepted" or "Edited" verdict in
`human_review/review_log.csv`. See `human_review/responsible_ai_log.md`
for concrete cases where this review step caught a wrong or hallucinated
AI answer.
