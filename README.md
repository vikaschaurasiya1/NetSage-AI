# NetSage AI

### AI-Assisted Network Troubleshooting & Responsible AI Review

**Project 2 | Applied AI + Network Troubleshooting**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-red?logo=streamlit)](https://netsage-ai-vikas.streamlit.app/)
[![Source Code](https://img.shields.io/badge/Source%20Code-GitHub-black?logo=github)](https://github.com/vikaschaurasiya1/NetSage-AI)

---

## 🌐 Project Links

| Resource                     | Link                                    |
| ---------------------------- | --------------------------------------- |
| 🚀 **Live Demo**             | https://netsage-ai-vikas.streamlit.app/ |
| 💻 **Source Code**           | github.com/vikaschaurasiya1/NetSage-AI           |
| 📄 **Project Documentation** | Available in the repository             |
| 🎥 **Demo Video**            | Available in the `docs/` folder         |

> **Live Application:** The deployed Streamlit application can be accessed directly through the Live Demo link above.

---

## 📌 Overview

NetSage AI is an AI-assisted troubleshooting application designed for Cisco-style Packet Tracer labs.

It analyzes:

* Network symptoms
* Topology information
* `show` command output
* Configuration evidence

and proposes:

* **Likely root cause**
* **OSI layer**
* **Confidence level**
* **Supporting evidence**
* **Next diagnostic command**
* **Suggested fix steps**

However, **AI-generated diagnoses are never treated as final automatically**.

A human reviewer must **Accept, Edit, or Reject** every diagnosis before a fix can be considered final. No configuration or fix is automatically applied to a network device.

---

## 🎯 Objectives

The project was developed to demonstrate how AI can assist network troubleshooting while maintaining a **human-in-the-loop safety mechanism**.

The major objectives are:

1. Analyze common network troubleshooting scenarios.
2. Generate structured AI-based diagnoses.
3. Provide evidence-based troubleshooting suggestions.
4. Independently validate configuration mistakes using deterministic rules.
5. Require human review before accepting an AI diagnosis.
6. Record reviewer decisions and corrections.
7. Evaluate AI-versus-human agreement.
8. Provide an interactive web interface for demonstration.

---

## 🏗️ Project Structure

```text
NetSage_AI/
│
├── README.md
├── app.py                              Streamlit web application
├── requirements.txt                    Python dependencies
├── Dockerfile                          Container configuration
├── Procfile                            Deployment configuration
│
├── cases.csv                           30 troubleshooting cases
│
├── prompts/
│   └── diagnose_prompt.md              System + user prompt,
│                                       JSON schema, examples,
│                                       batch-mode prompt and
│                                       reviewer-assist prompt
│
├── checker/
│   ├── rule_checker.py                 Deterministic configuration checks
│   ├── checker_output.csv              Per-case checker results
│   └── sample_output.txt               Sample console output
│
├── ai_diagnosis/
│   ├── run_diagnosis.py                Anthropic API batch runner
│   └── ai_responses.json               Saved AI diagnoses for 30 cases
│
├── human_review/
│   ├── review_log.csv                  Case-by-case review verdicts
│   └── responsible_ai_log.md           Analysis of cases requiring
│                                       human correction
│
├── dashboard/
│   └── NetSage_AI_Dashboard.xlsx       Case summaries, charts and
│                                       AI-vs-human agreement analysis
│
└── docs/
    └── demo_video_script.md             Demo video script
```

---

## 🔄 How the System Works

The project follows a structured troubleshooting workflow:

### 1. Collect Network Cases

`cases.csv` contains **30 troubleshooting cases** covering areas such as:

* VLAN
* Gateway
* DHCP
* DNS
* Routing
* ACL
* NAT
* Wireless
* IPv6
* HSRP
* VTP
* Port Security
* CDP

### 2. Generate Structured Prompts

`prompts/diagnose_prompt.md` defines the instructions used by the AI.

The prompt requires structured JSON containing:

```text
root_cause
confidence
evidence
next_command
fix_steps
```

Three worked examples are also included to guide the diagnosis format.

### 3. Run Deterministic Rule Checks

`checker/rule_checker.py` performs independent non-AI validation.

It checks for:

* Duplicate IP addresses
* Incorrect subnet masks
* Gateway mismatches
* Interfaces being down
* Missing VLANs
* Missing or invalid routes

These checks provide an additional validation layer independent of the AI.

### 4. Generate AI Diagnosis

`ai_diagnosis/run_diagnosis.py` sends the troubleshooting cases to the Anthropic API using the structured diagnosis prompt.

The generated results are stored in:

```text
ai_diagnosis/ai_responses.json
```

### 5. Human Review

Every diagnosis is reviewed by a human.

Each case receives one of three verdicts:

```text
Accepted
Edited
Rejected
```

Reviewer decisions are stored in:

```text
human_review/review_log.csv
```

Cases requiring correction are documented in:

```text
human_review/responsible_ai_log.md
```

### 6. Dashboard & Web Application

The project includes both:

* An analytical Excel dashboard
* A deployed Streamlit web application

The dashboard summarizes severity, OSI layers, concepts and AI-versus-human agreement.

The Streamlit application provides an interactive interface for demonstrating the troubleshooting workflow.

---

## 📊 Key Results

| Metric                              |        Result |
| ----------------------------------- | ------------: |
| **Total cases**                     |            30 |
| **Accepted as-is**                  |      22 (73%) |
| **Edited by reviewer**              |             7 |
| **Rejected by reviewer**            |             1 |
| **AI-vs-human agreement**           |           73% |
| **Deterministic rule-checker hits** | 8 of 30 (27%) |

The human-review process identified **8 cases requiring correction**, including cases where the AI produced incorrect or hallucinated conclusions.

This demonstrates why AI-generated troubleshooting recommendations should not be applied to network infrastructure without appropriate human validation.

---

## 🛡️ Responsible AI & Safety

Human review is a **hard requirement** of this project.

AI-generated `fix_steps` are never considered final unless the corresponding diagnosis has received either:

```text
Accepted
```

or

```text
Edited
```

in:

```text
human_review/review_log.csv
```

No AI-generated fix is automatically executed against a network device.

The responsible-AI analysis documents cases where human review identified incorrect or hallucinated AI responses, including **NET-013** and **NET-024**.

---

## 🚀 Live Deployment

NetSage AI is deployed using **Streamlit Community Cloud**.

### Live Application

**https://netsage-ai-vikas.streamlit.app/**

The application can be opened directly in a web browser without installing the project locally.

### Deployment Stack

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
Python 3.12
   ↓
Streamlit Application
   ↓
NetSage AI
```

---

## ⚙️ Local Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd NetSage-AI
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will then be available locally through the URL shown by Streamlit.

---

## 🤖 Reproducing the AI Diagnosis Run

If an Anthropic API key is available:

```bash
export ANTHROPIC_API_KEY=sk-...
cd ai_diagnosis
python3 run_diagnosis.py ../cases.csv --prompt ../prompts/diagnose_prompt.md
```

If no API key is configured, the project can still be evaluated using the saved:

```text
ai_diagnosis/ai_responses.json
```

---

## 🔍 Reproducing the Rule Checker

Run:

```bash
cd checker
python3 rule_checker.py ../cases.csv --out checker_output.csv
```

The checker operates independently of the AI diagnosis system.

---

## 📁 Documentation

Additional project documentation is available in the repository, including:

* Project report
* Responsible AI analysis
* Dashboard
* Demo video script
* AI diagnosis results
* Human review records

---

## 🎥 Demonstration

The demonstration covers:

1. Project overview
2. Network troubleshooting case
3. AI diagnosis
4. Deterministic rule checking
5. Human review
6. Diagnosis acceptance/correction
7. Dashboard/results
8. Live deployed application

The detailed shot-by-shot demonstration script is available at:

```text
docs/demo_video_script.md
```

---

## 🔮 Future Scope

Potential improvements include:

* Integration with real network devices in a controlled environment
* Additional deterministic validation rules
* More network protocols and troubleshooting scenarios
* Improved AI evaluation metrics
* Role-based reviewer authentication
* Persistent review database
* Automated regression testing
* Integration with network simulation platforms
* Enhanced monitoring and audit logging

---

## 👨‍💻 Project Information

**Project:** NetSage AI
**Domain:** Applied AI + Network Troubleshooting
**Application:** Streamlit
**AI Integration:** Anthropic API
**Deployment:** Streamlit Community Cloud
**Dataset:** 30 Cisco-style troubleshooting cases

---

## 📜 Safety Notice

NetSage AI is an **AI-assisted troubleshooting and educational application**.

It does not automatically modify network devices or execute AI-generated fixes.

All AI-generated troubleshooting recommendations must be reviewed by a human before being considered final.
