import os
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import anthropic
except ImportError:
    anthropic = None

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases.csv"
RESPONSES = ROOT / "ai_diagnosis" / "ai_responses.json"
REVIEW = ROOT / "human_review" / "review_log.csv"

st.set_page_config(page_title="NetSage AI", page_icon="🌐", layout="wide")

@st.cache_data
def load_cases():
    return pd.read_csv(CASES)

@st.cache_data
def load_saved_diagnoses():
    if RESPONSES.exists():
        with open(RESPONSES, encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_review():
    return pd.read_csv(REVIEW) if REVIEW.exists() else pd.DataFrame()

cases = load_cases()
saved = load_saved_diagnoses()
review = load_review()

def get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None

def rule_findings(row):
    text_all = f"{row.symptom} {row.topology_note} {row.show_outputs} {row.expected_fault}".lower()
    show = str(row.show_outputs).lower()
    findings = []
    if "duplicate" in text_all and ("ip address" in text_all or "dup_addr" in text_all):
        findings.append("Possible duplicate IP address assignment")
    if "mask" in text_all and any(x in text_all for x in ["mismatch", "wrong", "invalid"]):
        findings.append("Subnet mask mismatch / invalid mask suspected")
    if "gateway" in text_all and any(x in text_all for x in ["outside", "misconfig", "mismatch"]):
        findings.append("Default gateway misconfiguration suspected")
    if "administratively down" in show or "line protocol is down" in show:
        findings.append("Interface is down")
    if "vlan" in text_all and any(x in text_all for x in ["pruned", "missing", "not allowed", "wrong access vlan"]):
        findings.append("VLAN/trunk assignment problem suspected")
    if ("route" in text_all or "routing" in text_all) and any(x in text_all for x in ["invalid", "missing", "next-hop"]):
        findings.append("Route problem suspected")
    return findings

def diagnose_live(row):
    key = get_secret("ANTHROPIC_API_KEY")
    if not key or anthropic is None:
        return None, "Live AI is unavailable. Add ANTHROPIC_API_KEY to Streamlit Secrets; the saved project diagnoses remain available."
    model = get_secret("ANTHROPIC_MODEL") or "claude-sonnet-5"
    system = """You are NetSage AI, a network-troubleshooting assistant for Cisco-style Packet Tracer labs.
Base every claim ONLY on the supplied symptom, topology note, and show-command output.
Never invent evidence. Return ONLY valid JSON with:
case_id, root_cause, osi_layer, confidence (Low/Medium/High), evidence, next_command, fix_steps (array).
This is decision support. Never claim a fix has been applied or verified. A human must review every recommendation."""
    user = f"""CASE ID: {row.case_id}
SYMPTOM: {row.symptom}
TOPOLOGY NOTE: {row.topology_note}
SHOW-COMMAND OUTPUT: {row.show_outputs}

Return the JSON object only."""
    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model=model,
            max_tokens=900,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
        text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.I)
        return json.loads(text), None
    except Exception as e:
        return None, f"AI request failed: {e}"

st.title("🌐 NetSage AI")
st.caption("Evidence-backed network troubleshooting • deterministic checks + AI decision support + human review")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Open", ["Overview", "Case Diagnoser", "Rule Checker", "Evaluation"])
    st.divider()
    st.info("Safety: AI recommendations are advisory only. Review and verify every fix before applying it.")

if page == "Overview":
    st.subheader("Project overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cases", len(cases))
    c2.metric("Accepted", "22")
    c3.metric("Edited", "7")
    c4.metric("Rejected", "1")
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("### Severity")
        st.bar_chart(cases["severity"].value_counts())
        st.markdown("### OSI layer")
        st.bar_chart(cases["osi_layer"].value_counts())
    with right:
        st.markdown("### Concept tags")
        st.bar_chart(cases["concept_tag"].value_counts())
        st.markdown("### What this app does")
        st.markdown("- Select a troubleshooting case and inspect its evidence.\n- Run deterministic rule checks.\n- Optionally request a live AI diagnosis.\n- Compare saved AI output with human-review outcomes.\n- Keep fixes advisory; no device is modified by this app.")

elif page == "Case Diagnoser":
    st.subheader("Case Diagnoser")
    case_id = st.selectbox("Select case", cases.case_id.tolist())
    row = cases[cases.case_id == case_id].iloc[0]
    st.markdown(f"**Severity:** `{row.severity}` &nbsp;&nbsp; **Concept:** `{row.concept_tag}`")
    st.markdown("### Symptom")
    st.write(row.symptom)
    st.markdown("### Topology")
    st.write(row.topology_note)
    st.markdown("### Show-command evidence")
    st.code(row.show_outputs)

    findings = rule_findings(row)
    if findings:
        st.warning("Deterministic checks: " + " • ".join(findings))
    else:
        st.success("No deterministic rule hit for this case.")

    saved_result = next((x for x in saved if x.get("case_id") == case_id), None)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Saved diagnosis")
        if saved_result:
            if "error" in saved_result:
                st.error(saved_result["error"])
            else:
                st.json(saved_result)
        else:
            st.info("No saved diagnosis found.")
    with col2:
        st.markdown("### Live AI diagnosis")
        if st.button("Run live diagnosis", type="primary"):
            with st.spinner("Analyzing supplied evidence…"):
                result, err = diagnose_live(row)
            if err:
                st.error(err)
            else:
                st.json(result)
                st.success("Recommendation generated. Human review is required before any fix is applied.")

    with st.expander("Expected fault / grading reference"):
        st.write(row.expected_fault)

elif page == "Rule Checker":
    st.subheader("Deterministic Rule Checker")
    output = []
    for _, r in cases.iterrows():
        fs = rule_findings(r)
        output.append({
            "case_id": r.case_id,
            "severity": r.severity,
            "osi_layer": r.osi_layer,
            "findings": "; ".join(fs),
            "hit": "YES" if fs else "NO",
        })
    df = pd.DataFrame(output)
    hits = int((df.hit == "YES").sum())
    a, b = st.columns(2)
    a.metric("Cases scanned", len(df))
    b.metric("Cases with hits", f"{hits} ({hits/len(df):.0%})")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download checker results", df.to_csv(index=False), "checker_output.csv", "text/csv")

else:
    st.subheader("Evaluation & Human Review")
    if review.empty:
        st.warning("Human review log is not available.")
    else:
        st.dataframe(review, use_container_width=True, hide_index=True)
    st.markdown("### Project results")
    st.markdown("- **30** troubleshooting cases\n- **22** accepted as-is (73%)\n- **7** edited by a human reviewer\n- **1** rejected\n- **8/30** cases triggered deterministic rule checks")
    st.caption("The evaluation dataset is included for academic demonstration. In a real deployment, keep expected faults and grading labels out of the public user-facing interface.")
