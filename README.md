<div align="center">

<br />

<!-- Logo placeholder — replace with your actual logo asset -->
<img src="docs/aletheia.png" alt="Aletheia Logo" width="400" style="margin-bottom:8px" />

<h1>Aletheia: Clinical Workstation</h1>

<p><em>Evidence-grounded AI diagnostic reasoning, built for clinical precision.</em></p>

<br />

<!-- Stack badges — colors drawn from the Aletheia brand palette -->
![Python](https://img.shields.io/badge/Python_3.11+-162C41?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-162C41?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2.0-4F606F?style=flat-square&logo=databricks&logoColor=white)
![React](https://img.shields.io/badge/React_19-162C41?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-4F606F?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-162C41?style=flat-square&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4F606F?style=flat-square&logo=tailwindcss&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-162C41?style=flat-square&logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-4F606F?style=flat-square&logo=sqlite&logoColor=white)
[![License](https://img.shields.io/badge/License-Source--Available-162C41?style=flat-square)](LICENSE)

<br /><br />

</div>

---

## What is Aletheia?

Clinicians routinely juggle heterogeneous data, patient history, physical examination findings, laboratory panels, haematological morphology, and imaging results, across disconnected systems. This fragmentation introduces risk: relevant findings get overlooked, evidence retrieval is inconsistent, and diagnostic reasoning is not reproducible across encounters.

**Aletheia: Clinical Workstation** consolidates all clinical inputs into a single structured workspace and delegates synthesis to a purpose-built AI reasoning pipeline powered by **Google Gemini**. It returns a fully structured, versioned, and citation-verified differential diagnosis report within a single session, no cloud account required, no data leaving your machine.

Designed for individual clinical practitioners, research fellows, and academic departments evaluating AI-assisted diagnostic reasoning. Available as a standalone desktop application or deployed locally as a web application.

---

## Screenshots

### Casebook — Case Management Dashboard
> _Browse, search, tag, and archive all clinical cases from a single disciplined interface._


![Screenshot](docs/05.png)

<sub>↑ Casebook listing with active/archived state.</sub>

---

### Clinical Workspace — Split-Pane Data Entry & Report View
> _Structured clinical input forms alongside a live-rendered AI report — side by side._


![Screenshot](docs/04.png)

<sub>↑ Left panel: Anamnesis, Physical Exam, Laboratory, and Morphological data forms. Right panel: Rendered structured report with inline citations.</sub>

---

### Differential Diagnosis & Evolution Tracker
> _Version-controlled differential diagnosis with confidence shifts and rank movement across report iterations._


![Screenshot](docs/03.png)

<sub>↑ Differential evolution timeline comparing V1 → V2 → V3 with certainty bands and evidence counts.</sub>

---

### Report Viewer — Citation-Verified Output
> _Editorial-grade, fully structured clinical reports with PubMed-verified inline citations._


![Screenshot](docs/02.png)
![Screenshot](docs/01.png)

<sub>↑ Report rendered in TeX Gyre Termes with Vancouver-formatted references, confidence bars, and severity indicators.</sub>

---

## Core Features

**Case Management**: Full CRUD lifecycle for clinical cases with soft-archival, permanent deletion, and tag-based classification. Clinical sections (Anamnesis, Physical Exam, Laboratory, Morphological Data) are stored as typed JSON aggregates.

**AI Reasoning Pipeline**: A ten-stage orchestrated reasoning engine (`ReasoningOrchestrationService`) that performs deterministic preprocessing, structured prompt assembly, Gemini inference, response parsing, citation verification against PubMed E-utilities, deduplication, certainty policy enforcement, language enhancement, and immutable version persistence.

**PubMed Evidence Grounding**: Asynchronous NCBI E-utilities client with rate-limit enforcement, exponential back-off, per-PMID cache-stampede prevention, and automatic fallback metadata. Every citation in the report is verified against PubMed.

**Evidence Cache**: Global SHA-256-keyed evidence cache that de-duplicates grounding API calls across all cases, reducing redundant Gemini calls. Configurable TTL with soft-invalidation support.

**Follow-Up Timeline**: Append-only delta event system recording incremental clinical updates per case for longitudinal tracking without duplicating the full case state.

**Report Version History**: Immutable, append-only structured report snapshots with per-case versioning, differential evolution tracking, and multi-dimensional confidence scoring.

**Export Services**: One-click PDF export (via ReportLab with TeX Gyre Termes typography) and PowerPoint export (via python-pptx), both served as file streams.

**Settings Management**: Runtime key-value settings store managing API keys, grounding toggles, cache TTL, and export preferences, no schema migrations required.

---

## Prerequisites

Ensure the following tools are available in your system `PATH`:

| Tool | Minimum Version | Check |
|:---|:---|:---|
| Python | 3.11 | `python --version` |
| Node.js | 18.0 | `node --version` |
| npm | 9.0 (bundled with Node 18) | `npm --version` |
| Git | Any | `git --version` |

---

## Installation

Aletheia is available both as a standalone desktop application and as a locally-hosted web application.

### Option 1: Desktop Application (Linux)

1. Navigate to the **Releases** page of this repository.
2. Download the latest `.zip` release file for your Linux system.
3. Extract the `.zip` archive.
4. From the extracted folder, you can either:
   - Run the `.AppImage` directly.
   - Run the `./install.sh` script to install Aletheia to your system's applications menu. (You can remove it later using `./uninstall.sh`).

> **Note:** The desktop version is a self-contained application that bundles the required dependencies. You will still need an API key for Google Gemini.

---

### Option 2: Local Web Application

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/clinical-workstation.git
cd clinical-workstation
```

#### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and set your API key:

```env
# Required — get yours at https://aistudio.google.com
GEMINI_API_KEY=your_gemini_api_key_here

# Optional — upgrades PubMed rate limit from 3 req/s to 10 req/s
# Register at https://www.ncbi.nlm.nih.gov/account/
NCBI_API_KEY=your_ncbi_api_key_here
```

> **Note:** You can also set the Gemini API key after launch via the in-app **Settings** page (`/settings`), which writes the value to the local database at runtime.

#### 3. Launch

```bash
python launcher.py
```

That's it. The launcher handles everything automatically:

1. Validates Python 3.11+ and Node 18+ in your PATH
2. Creates `backend/.venv` Python virtual environment
3. Installs all Python dependencies from `backend/requirements.txt`
4. Installs frontend npm dependencies from `frontend/package.json`
5. Resolves any port conflicts on `8000` and `5173`
6. Starts the FastAPI backend (Uvicorn) and Vite dev server in parallel
7. Opens `http://localhost:5173` in your default browser after a 3-second grace period

#### Launcher options

```bash
# Start without auto-opening the browser
python launcher.py --no-browser
```

---

## Manual Setup (without the launcher)

For development scenarios where you want full control:

**Backend**
```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables Reference

All variables go in `backend/.env`. Copy `backend/.env.example` as your starting point.

| Variable | Required | Default | Description |
|:---|:---:|:---|:---|
| `GEMINI_API_KEY` | ✅ | _(empty)_ | Google Gemini API key for AI inference |
| `NCBI_API_KEY` | ☐ | _(empty)_ | NCBI PubMed key — upgrades rate limit to 10 req/s |
| `DEBUG` | ☐ | `false` | Enable debug mode |
| `LOG_LEVEL` | ☐ | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATABASE_URL` | ☐ | `sqlite+aiosqlite:///./clinical_workstation.db` | Database connection string |
| `GEMINI_MODEL` | ☐ | `gemini-3.1-flash-lite` | Gemini reasoning model |
| `GEMINI_GROUNDING_ENABLED` | ☐ | `true` | Enable PubMed search grounding |
| `MAX_EVIDENCE_CACHE_AGE_HOURS` | ☐ | `72` | Evidence cache TTL in hours |
| `PDF_OUTPUT_DIR` | ☐ | `./exports` | Directory for generated PDF/PPTX exports |
| `BACKEND_HOST` | ☐ | `0.0.0.0` | Host to bind the backend server |
| `BACKEND_PORT` | ☐ | `8000` | Backend server port |
| `CORS_ORIGINS` | ☐ | `http://localhost:5173` | Allowed CORS origins (comma-separated) |

---

## Architecture Overview

```
clinical-workstation/
│
├── launcher.py                  # Unified bootstrapper - single entry point
│
├── backend/                     # Python / FastAPI server
│   ├── main.py                  # App factory, lifespan, CORS, route registration
│   ├── requirements.txt
│   ├── .env.example             # Environment variable template
│   └── app/
│       ├── core/
│       │   ├── config.py        # pydantic-settings Settings class
│       │   ├── database.py      # Async SQLAlchemy engine, session factory, init_db()
│       │   └── logging.py       # loguru configuration
│       ├── models/              # SQLAlchemy ORM models
│       │   ├── case.py          # Case (JSON columns for clinical sections)
│       │   ├── report_version.py
│       │   ├── follow_up_entry.py
│       │   ├── evidence_cache.py
│       │   └── app_settings.py
│       ├── schemas/             # Pydantic request/response schemas
│       ├── api/
│       │   ├── router.py        # API v1 router aggregator
│       │   └── routes/          # cases, follow_ups, reasoning, export, admin
│       ├── services/            # Business logic layer
│       │   ├── case_service.py
│       │   ├── reasoning_service.py   # 10-stage orchestration facade
│       │   ├── pubmed_client.py       # NCBI E-utilities async client
│       │   ├── evidence_cache_service.py
│       │   ├── pdf_export_service.py
│       │   └── pptx_export_service.py
│       └── reasoning/
│           ├── prompts.py       # Structured prompt assembly
│           ├── parser.py        # JSON extraction + json-repair
│           ├── preprocessing.py # Deterministic lab/exam heuristics
│           ├── certainty.py     # Certainty policy enforcement
│           ├── grounding.py     # Gemini search grounding service
│           └── providers/       # AI provider abstraction (GeminiProvider)
│
└── frontend/                    # React 19 / TypeScript SPA
    └── src/
        ├── App.tsx              # React Router shell
        ├── pages/               # CasebookPage, NewCasePage, CaseWorkspacePage, SettingsPage
        ├── components/
        │   ├── layout/          # AppShell, WorkspaceSplitPane, ClinicalInputPanel
        │   ├── report/          # ReportRenderer, ReportVersionList, ConfidenceBar, etc.
        │   ├── timeline/        # TimelinePanel, TimelineEntry, AddFollowUpModal
        │   ├── forms/           # AnamnesisForm, PhysicalExamForm, LaboratoryForm, MorphologicalForm
        │   ├── casebook/        # CaseCard, EmptyState
        │   └── ui/              # Spinner, Toast, SplashScreen, ErrorBanner, LoadingSkeleton
        ├── stores/              # Zustand + Immer: caseStore, reportStore, settingsStore, uiStore
        ├── api/                 # Typed fetch wrappers: cases, reasoning, export, followUps, settings
        └── types/               # TypeScript interfaces for all domain entities
```

**Request flow:**

```
Browser (React SPA)
  → Zustand Store (async actions)
    → API Client (fetch wrapper → /api/v1)
      → Vite Dev Proxy (→ localhost:8000)
        → FastAPI Router
          → Route Handler (Pydantic validation, DB session injection)
            → Service Layer (business logic)
              → SQLAlchemy AsyncSession (SQLite)
              → Google Gemini API
              → NCBI PubMed E-utilities
```

---

## API Documentation

The FastAPI backend auto-generates interactive documentation at runtime:

| Interface | URL |
|:---|:---|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| Health check | `http://localhost:8000/api/health` |

---

## Running Tests

```bash
# Activate the virtual environment first
source backend/.venv/bin/activate   # macOS / Linux
# or: backend\.venv\Scripts\activate   # Windows

# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run all tests
cd backend && pytest

# Run a specific test file
pytest tests/test_pubmed_client.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

---

## Production Build

**Frontend**
```bash
cd frontend
npm run build
# Output: frontend/dist/

# Preview the production build locally
npm run preview
```

**Backend (with Gunicorn)**
```bash
cd backend
source .venv/bin/activate
pip install gunicorn

gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

> ⚠️ **Remove the `--reload` flag for production.** Use Gunicorn for process supervision instead.

---

## Technology Stack

| Layer | Technology | Role |
|:---|:---|:---|
| Bootstrapper | Python 3.11+ (`launcher.py`) | Environment validation, venv, npm install, port resolution, process supervision |
| Web Framework | FastAPI ≥ 0.111 | Async ASGI framework, OpenAPI generation, Pydantic integration |
| ASGI Server | Uvicorn[standard] ≥ 0.29 | Production ASGI server with uvloop and httptools |
| ORM | SQLAlchemy 2.0 (async) | AsyncSession, Mapped columns, async query execution |
| DB Driver | aiosqlite ≥ 0.20 | Non-blocking asyncio-compatible SQLite driver |
| Data Validation | Pydantic v2 | All request/response bodies, DTOs, settings |
| Configuration | pydantic-settings ≥ 2.0 | Type-safe `.env` management |
| LLM Provider | google-genai ≥ 1.0 | Gemini inference + search grounding |
| HTTP Client | httpx ≥ 0.27 | Async client for PubMed E-utilities |
| Retry Logic | tenacity ≥ 8.0 | Exponential back-off for API calls |
| PDF Export | ReportLab ≥ 4.0 | Structured clinical PDF with custom typography |
| PPTX Export | python-pptx ≥ 0.6.23 | PowerPoint report export |
| Logging | loguru ≥ 0.7 | Structured logging with rotation and gzip compression |
| JSON Repair | json-repair ≥ 0.30 | Fault-tolerant LLM JSON output recovery |
| Frontend Framework | React 19 + TypeScript | SPA |
| Build Tool | Vite | Dev server with API proxy, production build |
| Styling | Tailwind CSS | Semantic design token system (`clinical.*`, `aletheia.*` namespaces) |
| State Management | Zustand + Immer | Global domain state with mutation-style updates |
| Animation | Framer Motion 12 | Splash screen, panel reveals, physics-based transitions |
| UI Font | IBM Plex Sans | Clinical, serious tone |
| Report Font | EB Garamond | Editorial, scholarly report rendering |

---

## Design System

Aletheia uses a canonical brand palette designed for clinical precision and trust:

| Token | Hex | Usage |
|:---|:---|:---|
| `--aletheia-navy` | `#162C41` | Primary text, headings, interactive states |
| `--aletheia-slate` | `#4F606F` | Secondary text, subheadings |
| `--bg-primary` | `#F5F8FB` | Page background |
| `--border-default` | `#D7E2EC` | Default borders and dividers |
| `--state-stable` | `#3E6B61` | Stable diagnostic state indicator |
| `--state-evolving` | `#C58A2B` | Evolving diagnostic state indicator |
| `--confidence-high` | `#244B73` | High-confidence differential display |

The design philosophy: **clinical, elegant, precise, restrained.** No rounded pills, no neon gradients, no startup aesthetic. Every component is designed to feel like a precision instrument.

---

## Roadmap

**Near-term**
- [ ] OS keychain integration for secrets management (replace `.env` plaintext storage)
- [ ] Gemini streaming responses with progressive report section rendering
- [ ] Thread pool execution for PDF/PPTX export (prevent event-loop blocking)

**Mid-term**
- [ ] PostgreSQL migration with asyncpg (unblock concurrent writes)
- [ ] Alembic migration pipeline for schema evolution
- [ ] JWT-based authentication middleware for shared/network deployments
- [ ] Comprehensive pytest-asyncio test suite

**Long-term**
- [ ] Multi-user / multi-tenant architecture with row-level isolation
- [ ] OpenTelemetry observability stack (Jaeger / Tempo)
- [ ] Additional AI provider backends (Claude, GPT-4o) via `BaseAIProvider` abstraction
- [ ] Docker Compose deployment (FastAPI + PostgreSQL + Nginx)

---

## License

Custom: see [LICENSE](LICENSE) for details.

---

<div align="center">
<sub>Built with rigor. Designed for clinical practice.</sub>
</div>
