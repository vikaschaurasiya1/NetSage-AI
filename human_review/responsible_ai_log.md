# Responsible AI Log — NetSage AI

This log documents every case where a human reviewer changed or rejected
the AI's diagnosis, and why. Its purpose is to make the assistant's
failure modes visible, not to hide them. It also documents our human
oversight process: every one of the 30 cases was reviewed and marked
**Accepted**, **Edited**, or **Rejected** before being treated as a valid
diagnosis (see `human_review/review_log.csv` for the full log).

**Summary:** 22 Accepted · 7 Edited · 1 Rejected (8 of 30 cases, ~27%,
required a human correction of some kind).

---

## 1. NET-009 — Host Default Gateway IP Misconfiguration
- **AI said:** Likely a DNS resolution issue, Low confidence, recommended
  flushing DNS cache.
- **What actually happened:** The topology note plainly shows the router
  gateway is 192.168.1.1, but the host is configured with 192.168.1.254 —
  a simple gateway typo. The AI had the relevant fact in front of it but
  reached for a less-likely, evidence-poor explanation instead.
- **Correction:** Reviewer identified the gateway mismatch directly, set
  root cause to "Host Default Gateway IP Misconfiguration," and raised
  confidence to High.
- **Lesson:** When a case mentions two device configs, explicitly diff
  them before diagnosing rather than pattern-matching to a common
  Layer-7 symptom.

## 2. NET-013 — Switch Port Assigned to Wrong Access VLAN
- **AI said:** Guessed a trunk misconfiguration between switches, with no
  specific evidence line cited.
- **What actually happened:** The show output directly states
  `switchport access vlan 14` on the Finance PC's port, versus the
  expected VLAN 40 — an access-port problem, not a trunk problem.
- **Correction:** Reviewer rejected the trunk theory and pointed the
  diagnosis at the actual access-VLAN line.
- **Lesson:** The AI must ground every hypothesis in a quoted line from
  the show output (per the prompt's evidence rule) — it should not have
  been allowed to submit a diagnosis with no supporting quote.

## 3. NET-021 — OSPF Redistribution Missing 'subnets' Keyword
- **AI said:** OSPF process ID mismatch between routers.
- **What actually happened:** Only one process ID appears anywhere in the
  case; there is no second router config to compare it against. The real,
  evidenced issue is the missing `subnets` keyword on the `redistribute`
  line, which silently drops classless routes.
- **Correction:** Reviewer corrected the root cause and flagged that the
  AI's explanation referenced a comparison that wasn't actually possible
  from the given evidence.
- **Lesson:** Flag (and ideally block) diagnoses that imply evidence
  that isn't present in the case.

## 4. NET-024 — VTP Domain Name Case Mismatch
- **AI said:** VTP password mismatch.
- **What actually happened:** No password appears anywhere in the case
  evidence — the AI invented this detail. The real, evidenced fault is a
  case-sensitive VTP domain name mismatch (`CORP` vs `corp`).
- **Correction:** Reviewer rejected the hallucinated "password" detail
  and corrected the root cause to the domain case mismatch.
- **Lesson:** This is the clearest hallucination in the dataset — a
  invented artifact not grounded in the case at all. It's the strongest
  argument in this project for mandatory human review before any fix is
  applied to a live/lab device.

## 5. NET-027 — HSRP Timer Mismatch
- **AI said:** Priority values (110 vs 100) too close together, causing
  flapping.
- **What actually happened:** HSRP does not re-elect Active on priority
  alone once a router is Active (no preempt behavior implied here); the
  evidenced cause is the mismatched hello timers (3s vs 10s), which
  causes the standby to falsely believe the active has failed.
- **Correction:** Reviewer corrected the root cause to the timer
  mismatch.
- **Lesson:** The AI needs a protocol-behavior check, not just a
  "biggest visible number difference" heuristic — priority and timer
  values look superficially similar but have very different failure
  mechanics.

## 6. NET-003 — DNS Failure (Rejected pending clarification)
- **AI said:** DNS lookups fail due to the domain-lookup/name-server
  config being "not active," Medium confidence.
- **What actually happened:** The evidence phrase "not active" is
  ambiguous — it isn't clear whether it refers to the `ip domain-lookup`
  config state or to the DNS server process itself. The AI treated an
  ambiguous log fragment as if it clearly supported one interpretation.
- **Correction:** Reviewer **rejected** this diagnosis rather than
  accepting a guess, and requested an additional `show running-config`
  / DNS server status check before re-diagnosing.
- **Lesson:** Ambiguous evidence should lower confidence AND should be
  flagged for a clarifying command — not just hedged with a "Medium"
  label while still committing to one specific story.

## 7. NET-015 — Invalid Static Route Next-Hop (confidence edited up)
- **AI said:** Correct root cause, but Medium confidence.
- **Correction:** Reviewer raised confidence to High — the evidence
  ("Next-hop IP 10.0.0.5 unreachable") is an explicit, checkable fact,
  not an inference.
- **Lesson:** Confidence calibration matters as much as root-cause
  accuracy; under-confidence on solid evidence wastes reviewer time
  double-checking things that don't need it.

## 8. NET-019 — Native VLAN Mismatch (urgency framing edited)
- **AI said:** Correct root cause, High confidence, framed with
  security-incident urgency.
- **Correction:** Reviewer kept the technical diagnosis but toned down
  the write-up — this case is tagged Low severity in the dataset (a
  logging/hygiene issue, not an active outage or breach).
- **Lesson:** Technical correctness and appropriate urgency framing are
  separate things the reviewer has to check independently.

---

## What this log demonstrates about the safety rule

Per the problem statement's safety rule ("human review"), none of the 8
corrections above were ever applied to a device. They were caught during
the **Accepted / Edited / Rejected** review step, before any fix_steps
were acted on. The clearest cases (NET-013's missing evidence and
NET-024's invented password) show concretely why an AI suggestion must
never be auto-applied to real or simulated network equipment.
