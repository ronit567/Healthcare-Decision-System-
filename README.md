# AI Referral Intake & Decision System

A full-stack healthcare AI system that processes patient referrals through an AI pipeline and produces admission recommendations. Inspired by modern healthcare AI startups (ExaCare-style architecture).

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│   Frontend   │     │              Backend (FastAPI)                │
│   (Next.js)  │────▶│                                              │
│              │     │  ┌──────────────────────────────────────┐    │
│ • Inbox      │     │  │   Workflow Engine (Step Functions)    │    │
│ • Detail     │     │  │                                      │    │
│ • Workflow   │     │  │  Ingest → Extract → Normalize →      │    │
│ • Decision   │     │  │  Risk Score → Insurance → Decision → │    │
│ • Logs       │     │  │  Store                               │    │
│              │     │  └──────────────────────────────────────┘    │
└─────────────┘     │                                              │
                    │  ┌────────────┐  ┌────────────────────────┐  │
                    │  │  LLM Svc   │  │   Rules Engine         │  │
                    │  │  (OpenAI)  │  │   (Deterministic)      │  │
                    │  └────────────┘  └────────────────────────┘  │
                    │                                              │
                    │  ┌────────────┐  ┌────────────────────────┐  │
                    │  │ PostgreSQL │  │  DynamoDB Mock          │  │
                    │  │ (Truth)    │  │  (Logs/State)           │  │
                    │  └────────────┘  └────────────────────────┘  │
                    └──────────────────────────────────────────────┘
```

## Tech Stack

- **Backend:** Python / FastAPI
- **Frontend:** Next.js (App Router) / React / TailwindCSS / Lucide Icons
- **Databases:** PostgreSQL (source of truth) + DynamoDB mock (execution logs)
- **LLM:** OpenAI GPT-4o-mini (structured JSON outputs)
- **Architecture:** Serverless / event-driven (simulated Lambda + Step Functions)

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes + Pydantic schemas
│   │   ├── database/       # PostgreSQL models + DynamoDB mock
│   │   ├── services/       # LLM service + Rules engine
│   │   └── workflow/       # Step Functions engine + 7 Lambda handlers
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages (Inbox, New, Detail, Logs)
│       ├── components/     # Sidebar, Card, Badge
│       └── lib/            # API client + TypeScript types
└── README.md
```

## Workflow Pipeline

Each step is a stateless Lambda-style handler:

| Step | Description | Type |
|------|-------------|------|
| `ingestReferral` | Validate and structure raw referral input | Logic |
| `extractClinicalData` | LLM extracts diagnosis, mobility, comorbidities, etc. | LLM |
| `normalizeData` | Standardize and clean extracted fields | Logic |
| `riskScoring` | LLM assesses risk level + confidence score | LLM |
| `insuranceCheck` | Rule-based insurance verification | Rules |
| `generateDecision` | LLM + Rules hybrid → ACCEPT / REJECT / REVIEW | LLM + Rules |
| `storeResults` | Package final results for persistence | Logic |

## Rules Engine

Deterministic rules that influence/override LLM decisions:

- **Oxygen Required** → flags high acuity case
- **No Insurance** → automatic REJECT
- **Independent Mobility** → lower admission priority
- **High Risk + High Confidence** → flag for clinical review
- **Cognitive Impairment** → elevated care level

## Dual Database Architecture

- **PostgreSQL** (source of truth): patients, referrals, decisions, workflow runs
- **DynamoDB Mock** (operational): step execution logs, LLM outputs, workflow state

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and PostgreSQL connection string

# Create the database
createdb referral_system

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM calls |
| `DATABASE_URL` | PostgreSQL connection string |
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: http://localhost:8000/api) |

## Frontend Pages

- **Referral Inbox** (`/`) — List of all referrals with status, risk, and decision badges
- **New Referral** (`/new`) — Submission form with sample referral loader
- **Patient Detail** (`/referral/[id]`) — Full detail view with clinical data, insurance, rules, decision panel, and workflow trace
- **Observability Logs** (`/logs`) — Queryable execution logs across all workflows

## Sample Demo

1. Start backend and frontend
2. Navigate to `/new`
3. Click "Load Sample Referral" to populate a demo patient
4. Submit — the AI pipeline runs all 7 steps
5. View the result on the detail page with full decision reasoning
