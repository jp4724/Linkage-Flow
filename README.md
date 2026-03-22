# Linkage Flow

<p align="center">
  <img src="./Linkage_Flow_Icon.png" alt="Linkage Flow Icon" width="420" />
</p>

AI-powered networking and job-application assistant built with Streamlit, SQLite, and Gemini.

## Try the app (hosted)

**No install needed** — open the live Streamlit deployment:

**[https://linkage-flow.streamlit.app/](https://linkage-flow.streamlit.app/)**

The **app owner** should set `GEMINI_API_KEY` in **[Streamlit Community Cloud → app → Settings → Secrets](https://share.streamlit.io/)** so Gemini works for everyone using the link. Visitors can open the URL and use the UI without installing anything.

> **Note:** The cloud database is **ephemeral** (SQLite on Streamlit Cloud resets when the app restarts). For persistent contacts, run the app **locally** with `JAA.db` or connect a remote database.

---

## What This Project Does

Linkage Flow helps you automate high-value parts of your outreach workflow:
- Store and manage alumni/contact profiles in a local SQLite database.
- Generate personalized networking emails based on your background and target profile details.
- Keep prompts centralized in YAML for easier iteration on tone and behavior.
- Run everything from a single Streamlit app with a simple multi-tab interface.

---

## Demo

Screen recording of generating a personalized outreach email (fill **Self Information**, pick a contact, **Generate**, copy result):

<p align="center">
  <img src="./show.gif" alt="Demo: generating a tailored networking email in Linkage Flow" width="920" />
</p>

Place **`show.gif`** in the repository root next to `README.md` so the image loads on GitHub.

---

## Main Features

- **Profile + data workflow:** Manage records from uploaded CSVs and preview them in-app.
- **Personalized email generation:** Uses Gemini with prompt instructions tuned for short outreach emails.
- **Local-first architecture:** SQLite (`JAA.db`) — persistent when you run locally; on Streamlit Cloud the file is recreated when the app sleeps/restarts.
- **Prompt-driven behavior:** `prompts.yaml` controls LLM extraction and generation instructions.
- **API key management in UI:** Save `GEMINI_API_KEY` into `.env` from the Streamlit sidebar.
---

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- SQLite + SQLAlchemy
- Google Gemini API (`google-genai`)
- `python-dotenv`, `tenacity`, `PyYAML`
---

## Project Structure

```text
.
|-- app.py                    # Streamlit app entry point
|-- AI_func.py                # Gemini invocation + response parsing helpers
|-- generate_mail.py          # Prompted email generation function
|-- db_func.py                # SQLite read/write and sync utilities
|-- query.sql                 # SQL definitions (table creation, utility queries)
|-- prompts.yaml              # System instructions used by LLM features
|-- settings.py               # Paths and project constants
|-- logger_config.py          # Logging setup (console + rotating file)
|-- data/
|   |-- self.txt              # Your profile/resume text used for personalization
|   `-- JD.txt                # Job description input sample
`-- *.ipynb                   # Exploration/prototyping notebooks
```
---
## Quick Start

### 1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

**Local:** create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

You can also set this inside the app sidebar and click **Save Key**.

**Streamlit Community Cloud:** in the app **Settings → Secrets**, add:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

The app maps this into `os.environ` before loading Gemini-related modules.

### 4) Database

On startup, the app **creates `JAA.db` if missing** and runs the `create_alumni_table` statement from `query.sql` (via `db_func.ensure_alumni_table`). You can still run other statements in `query.sql` manually (e.g. in DB Browser) if needed.

- Database file: `JAA.db`
- Table: `alumni`

### 5) Run the app

```powershell
streamlit run app.py
```

Then open the local URL shown in terminal (typically `http://localhost:8501`).
---
## How To Use

1. **Self Information tab**
   - Paste/update your profile in `data/self.txt`.
2. **Database Management tab**
   - Upload profile CSV and manage records (ingestion pipeline placeholder is present).
3. **Email Generator tab**
   - Pick a target from database records and generate a tailored outreach email.
4. **Analytics tab**
   - View basic metrics (e.g., number of processed profiles).
---
## Notes and Current Limitations

- CSV ingestion pipeline UI exists, but extraction execution is currently a placeholder in `app.py`.
- `generate_mail.py` uses a specific preview model ID (`gemini-3-flash-preview`); update model IDs as needed for your account/availability.
- The code assumes `GEMINI_API_KEY` exists; app behavior is best when `.env` is configured before use.
---
## Security

- Never commit `.env` (already excluded in `.gitignore`).
- Keep API keys and personal contact data local/private.
---
## Roadmap Ideas

- Wire full CSV-to-structured-data extraction flow into the Streamlit ingestion button.
- Add automated tests for database and email-generation functions.
- Add tracking for sent emails and response outcomes.