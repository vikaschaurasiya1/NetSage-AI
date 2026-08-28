# NetSage AI — Deployment Ready

## Recommended: Streamlit Community Cloud

This repository is prepared as a Streamlit application.

### 1. Push the `NetSage_AI` folder to GitHub

Keep `app.py`, `requirements.txt`, `cases.csv`, `ai_diagnosis/`, `checker/`, and the other project folders in the repository.

### 2. Deploy

Open Streamlit Community Cloud and create an app from your GitHub repository.
Use:
- Branch: `main`
- Main file: `app.py`
- Python: 3.12

### 3. Configure the AI key

The app works without a live API key because it includes the saved diagnosis results.

For live AI diagnosis, add these secrets in the app settings:

```toml
ANTHROPIC_API_KEY = "your_key"
ANTHROPIC_MODEL = "claude-sonnet-5"
```

Never commit a real API key. The example file is `.streamlit/secrets.toml.example`.

### 4. Test

The deployed app provides:
- Overview dashboard
- Case Diagnoser
- Deterministic Rule Checker
- Saved AI diagnoses
- Optional live AI diagnosis
- Human-review/evaluation view

## Local run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Docker

```bash
docker build -t netsage-ai .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key netsage-ai
```

Then open `http://localhost:8501`.

## Important project safety behavior

The application does not connect to or modify a real network device. AI output is advisory and must be reviewed by a human before any configuration change is applied.

## Deployment files added

- `app.py` — production-style Streamlit entry point
- `requirements.txt` — pinned Python dependencies
- `Dockerfile` — container deployment
- `Procfile` — platforms that support process files
- `.streamlit/config.toml` — Streamlit server configuration
- `.streamlit/secrets.toml.example` — secret template
- `.gitignore` — prevents credentials and generated Python files from being committed
