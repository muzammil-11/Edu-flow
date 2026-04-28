# EduFlow — AI-Powered University Admissions System

EduFlow is a full-stack, multi-agent AI application that automates the end-to-end university admissions process — from application intake to offer letter dispatch. It uses a LangGraph state machine with six sequential AI agents, human-in-the-loop review for borderline cases, real-time WebSocket status updates, and a comprehensive admin dashboard.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Agent Pipeline](#agent-pipeline)
- [Eligibility Scoring](#eligibility-scoring)
- [Human-in-the-Loop Review](#human-in-the-loop-review)
- [Running Tests](#running-tests)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Overview

Traditional university admissions require weeks of manual effort — reviewing documents, scoring applications, scheduling interviews, and communicating decisions. EduFlow replaces this process with an automated AI pipeline that handles each step consistently, with full auditability and human oversight for edge cases.

A single application flows through six AI agents in sequence:

```
Intake → Verification → Eligibility → Interview → Decision → Dispatch
```

For borderline GPA cases (3.0–3.2), the workflow automatically pauses and routes to a human reviewer before continuing.

---

## Architecture

### System tiers

```
Browser (React)
    ↕  HTTP REST + WebSocket
FastAPI server
    ├── LangGraph orchestrator (6-node state machine)
    ├── Tesseract OCR + PyPDF (document extraction)
    └── FAISS + TF-IDF (program similarity scoring)
    ↕  Motor async driver
MongoDB
    ├── applications collection  (metadata + decisions)
    ├── documents collection     (OCR text + file info)
    └── LangGraph checkpoints    (full agent state per thread_id)
```

### Agent pipeline

Each application is assigned a unique `thread_id`. The LangGraph graph runs asynchronously via `asyncio.create_task`. The browser opens a WebSocket on that `thread_id` and receives live stage updates. When the workflow completes, the final decision is broadcast via WebSocket and written to MongoDB.

```
START
  └── intake_node          — validates and normalises form data
        └── verification_node   — OCR + GPT-4o document assessment
              └── eligibility_node    — FAISS score + GPT-4o verdict
                    ├── (score < 60)  → decision_node → dispatch_node → END
                    ├── (borderline)  → human_review_node → END (paused)
                    └── (score ≥ 60)  → interview_node → decision_node → dispatch_node → END
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Shadcn/UI, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.11, uvicorn |
| AI orchestration | LangGraph 1.0, LangChain |
| LLM | GPT-4o via `emergentintegrations` |
| Vector search | FAISS (faiss-cpu), scikit-learn TF-IDF |
| OCR | Tesseract (pytesseract) + PyPDF |
| Database | MongoDB 7, Motor (async), PyMongo (sync) |
| State persistence | langgraph-checkpoint-mongodb |
| Testing | pytest, requests |

---

## Project Structure

```
Edu-flow-main/
├── backend/
│   ├── agents/
│   │   ├── intake_agent.py          # Form validation and normalisation
│   │   ├── verification_agent.py    # Document OCR and GPT-4o assessment
│   │   ├── eligibility_agent.py     # FAISS scoring + GPT-4o verdict
│   │   ├── interview_agent.py       # Interview scheduling (mocked)
│   │   ├── decision_agent.py        # Admit / waitlist / deny logic
│   │   └── offer_agent.py           # Offer letter dispatch (mocked)
│   ├── services/
│   │   ├── vector_store.py          # FAISS index + TF-IDF scoring
│   │   ├── calendar_service.py      # Calendar service (mocked)
│   │   └── email_service.py         # Email service (mocked)
│   ├── tests/
│   │   └── test_university_workflow.py
│   ├── db_config.py                 # MongoDB + LangGraph checkpointer
│   ├── graph_builder.py             # LangGraph state machine definition
│   ├── server.py                    # FastAPI app, endpoints, WebSocket manager
│   ├── state_schema.py              # ApplicationState TypedDict
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── ApplicationForm.jsx
│   │   │   ├── ApplicationStatus.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── components/
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── ReviewQueue.jsx
│   │   │   └── ui/                  # Shadcn/UI component library
│   │   └── App.js
│   └── package.json
└── memory/
    └── PRD.md
```

---

## Prerequisites

The following must be installed on your machine before setup:

- **Python 3.11+**
- **Node.js 20+** and **yarn**
- **MongoDB 7** — running locally or accessible via URI
- **Tesseract OCR** — required for image document extraction

### Installing Tesseract

Tesseract is a system-level dependency and is not included in `requirements.txt`. Install it before running the backend.

**Ubuntu / Debian:**
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

**macOS (Homebrew):**
```bash
brew install tesseract
```

**Windows:**
Download the installer from the [Tesseract GitHub releases page](https://github.com/tesseract-ocr/tesseract/releases) and add it to your system PATH.

---

## Environment Variables

Create a file named `.env` inside the `backend/` directory with the following values:

```env
# Required — OpenAI API key (used via emergentintegrations)
EMERGENT_LLM_KEY=your_openai_api_key_here

# Required — MongoDB connection string
MONGO_URL=mongodb://localhost:27017

# Optional — MongoDB database name (defaults to test_database)
DB_NAME=eduflow

# Optional — allowed CORS origins (defaults to *)
CORS_ORIGINS=http://localhost:3000
```

Create a file named `.env` inside the `frontend/` directory:

```env
# Required — URL of the running FastAPI backend
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/Edu-flow.git
cd Edu-flow
```

### 2. Set up the backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create your .env file (see Environment Variables section above)
cp .env.example .env
# Then edit .env with your actual values
```

### 3. Set up the frontend

```bash
cd ../frontend

# Install Node dependencies
yarn install

# Create your frontend .env file
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
```

---

## Running the Application

### Start MongoDB

Make sure your MongoDB instance is running. If using a local installation:

```bash
mongod --dbpath /data/db
```

### Start the backend

```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. The interactive API docs are at `http://localhost:8000/docs`.

### Start the frontend

In a separate terminal:

```bash
cd frontend
yarn start
```

The React app will open at `http://localhost:3000`.

---

## API Reference

### Application endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/` | Health check |
| `POST` | `/api/applications` | Submit a new application |
| `GET` | `/api/applications/{thread_id}` | Get current application status |
| `POST` | `/api/documents/upload/{thread_id}` | Upload a document (PDF or image) |
| `GET` | `/api/documents/list/{thread_id}` | List documents for an application |
| `WS` | `/ws/{thread_id}` | WebSocket for real-time status updates |

### Admin endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/applications` | List all applications |
| `GET` | `/api/admin/pending-reviews` | Get applications awaiting human review |
| `POST` | `/api/admin/review/{thread_id}` | Submit a human review decision |
| `GET` | `/api/admin/analytics` | Admission analytics and GPA distribution |
| `GET` | `/api/admin/audit-log` | Full audit log with agent reasoning per application |

### Application submission body

```json
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone": "+91-9876543210",
  "program": "Computer Science",
  "gpa": 3.7,
  "test_scores": "SAT: 1450",
  "essay": "I am passionate about building software that helps people."
}
```

### Human review decision body

```json
{
  "approved": true,
  "comments": "Strong research background despite borderline GPA"
}
```

---

## Agent Pipeline

### Intake agent

Validates that all required fields are present and properly formatted. Normalises the submitted data (trims whitespace, validates GPA range, etc.) using GPT-4o.

### Verification agent

Fetches any uploaded documents from MongoDB, runs Tesseract OCR on image files (PNG, JPEG) and PyPDF on PDF files to extract text, then uses GPT-4o to assess whether each document appears genuine and complete. Sets `documents_verified` and `document_issues` on the state.

### Eligibility agent

The core scoring node. Computes a 100-point eligibility score using four components:

| Component | Weight | Basis |
|---|---|---|
| GPA score | 40 pts | GPA value against program minimum |
| FAISS similarity | 30 pts | TF-IDF vector match between applicant profile and program description |
| Essay quality | 15 pts | GPT-4o assessment of the personal statement |
| Test score | 15 pts | Normalised test score against program benchmark |

If the score is below 60, the applicant is routed to decision (denied). If GPA is in the 3.0–3.2 borderline range, the workflow is flagged for human review. Otherwise the applicant proceeds to the interview stage.

### Interview agent

Schedules an interview by computing `datetime.utcnow() + timedelta(days=7)` and writing the date to the application state. The calendar service and email invitation are currently mocked (they log to console only). See [Known Limitations](#known-limitations).

### Decision agent

Makes the final admission decision based on eligibility score:

- Score ≥ 75 → **admitted**
- Score 60–74 → **waitlisted**
- Score < 60 → **denied**

Augments the decision with GPT-4o reasoning that is stored in the audit log.

### Offer dispatch agent

Sends an offer letter to the applicant's email address. Currently mocked — logs to console. The email service is a drop-in replacement point for a real SMTP or SendGrid integration.

---

## Eligibility Scoring

The FAISS vector store is initialised at server startup in `services/vector_store.py`. Six program descriptions are encoded using TF-IDF with 500 features and stored in a FAISS flat index. When an application is scored, the applicant's essay and submitted data are combined into a query vector and matched against all six programs using cosine similarity.

**Supported programs and their minimum GPA requirements:**

| Program | Minimum GPA |
|---|---|
| Computer Science | 3.0 |
| Engineering | 3.0 |
| Business Administration | 2.8 |
| Medicine | 3.5 |
| Law | 3.2 |
| Arts and Humanities | 2.5 |

The FAISS index is rebuilt in memory on every server restart. It does not persist to disk between restarts.

---

## Human-in-the-Loop Review

When an applicant's GPA falls in the borderline range (3.0–3.2), the eligibility agent sets `requires_human_review = True` in the application state. The `route_after_eligibility` function in `graph_builder.py` routes the workflow to `human_review_node`, which sets the status to `pending_review` and terminates the current graph execution.

The application then appears in the admin dashboard under the **Reviews** tab. An administrator reviews the application details and submits a decision via `POST /api/admin/review/{thread_id}`:

```json
{ "approved": true, "comments": "Approved — strong recommendation letters" }
```

This calls `graph.update_state()` to inject the human decision into the saved checkpoint, then calls `resume_workflow()` to continue execution from the interview or decision node as appropriate.

The state persistence that makes this work is handled by `langgraph-checkpoint-mongodb`, which serialises the full `ApplicationState` TypedDict into a MongoDB collection keyed by `thread_id`.

---

## Running Tests

The test suite covers API health, application submission, status polling, admin endpoints, and human review flow.

```bash
cd backend
source venv/bin/activate

# Set the backend URL (defaults to the preview deployment URL in the test file)
export REACT_APP_BACKEND_URL=http://localhost:8000

# Run all tests
pytest tests/test_university_workflow.py -v

# Run a specific test class
pytest tests/test_university_workflow.py::TestApplicationSubmission -v
```

18 tests are included covering the following scenarios:

- API root health check
- High GPA application submission (GPA 3.8 — expected: admitted)
- Low GPA application submission (GPA 2.0 — expected: denied)
- Borderline GPA application (GPA 3.1 — expected: pending review)
- Application status retrieval
- Document upload (PDF and image)
- Admin application listing
- Pending review queue
- Analytics endpoint response structure
- Audit log format and content
- Human review approval and rejection

---

## Known Limitations

**Email service is mocked.** The offer dispatch agent and interview invitation both call `email_service.py`, which only prints to console. No emails are sent to applicants. To connect a real email provider, replace the print statements in `email_service.py` with an SMTP or SendGrid call.

**Calendar service is mocked.** The interview agent schedules interviews by adding 7 days to the current time. No real calendar event is created. The `interview_date` is stored in state but is not surfaced to the applicant in the React UI. The `CalendarService` class already exposes `schedule_interview`, `cancel_interview`, and `reschedule_interview` methods as stubs — these can be connected to Google Calendar or Calendly.

**FAISS index is in-memory only.** The vector store is rebuilt from hardcoded program descriptions every time the server starts. There is no persistence of the FAISS index to disk.

**WebSocket connection manager is not thread-safe.** The `ConnectionManager` stores active connections in a plain Python dict. Under high concurrent load, simultaneous broadcasts could cause race conditions. A production deployment should use a Redis-backed pub/sub bus instead.

**No authentication or authorisation.** All admin endpoints (`/api/admin/*`) are publicly accessible. A production deployment must add JWT-based authentication and role-based access control before exposing admin routes.

**No Docker setup.** The application must be set up manually. Tesseract in particular is a system-level dependency that is easy to miss. See [Prerequisites](#prerequisites).

---

## Roadmap

- [ ] Load testing for 100+ concurrent applications (identify thread pool and checkpointer bottlenecks)
- [ ] Playwright end-to-end tests covering the React frontend
- [ ] Docker Compose setup with backend, frontend, and MongoDB containers
- [ ] Real adaptive interview scheduling (Google Calendar / Calendly integration)
- [ ] Real email delivery (SendGrid / SMTP)
- [ ] FAQ chatbot for applicants using the existing FAISS vector store
- [ ] Bias detection dashboard in the admin panel
- [ ] JWT authentication for admin endpoints
- [ ] FAISS index persistence to disk
- [ ] Redis-backed WebSocket connection manager for concurrent safety
