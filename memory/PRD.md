# University Administration Workflow System - PRD

## Original Problem Statement
Build an Agentic AI-based University Administration Workflow System using Python, LangGraph (orchestration), FastAPI, React, and LLMs. The system automates application intake, document verification (OCR), eligibility screening (Vector DB), interview scheduling, decision generation, and offer letter dispatch. Human-in-the-loop for borderline applications with state persistence.

## Tech Stack
- **Frontend**: React + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI + Python
- **Database**: MongoDB (Motor async + PyMongo sync)
- **Orchestration**: LangGraph with MongoDB checkpointer
- **LLM**: OpenAI GPT-4o via emergentintegrations
- **OCR**: Tesseract (pytesseract + Pillow)
- **Vector DB**: FAISS with scikit-learn TF-IDF embeddings

## Architecture
```
/app/backend/
  agents/ - LangGraph agent nodes (intake, verification, eligibility, interview, decision, offer)
  services/ - Email (mock), Calendar (mock), Vector Store (FAISS)
  server.py - FastAPI endpoints
  graph_builder.py - LangGraph workflow definition
  state_schema.py - TypedDict state schema
  db_config.py - MongoDB + checkpointer config

/app/frontend/src/
  pages/ - LandingPage, ApplicationForm, ApplicationStatus, AdminDashboard
  components/ - DocumentUpload, ReviewQueue
```

## Completed Features
- [x] LangGraph multi-agent pipeline (Intake -> Verification -> Eligibility -> Interview -> Decision -> Offer)
- [x] Application submission and tracking with WebSocket real-time updates
- [x] Human-in-the-loop for borderline GPA applications (3.0-3.2 range)
- [x] Document upload with OCR text extraction (Tesseract for images, PyPDF for PDFs)
- [x] FAISS Vector DB eligibility scoring (TF-IDF, 6 programs, composite score: GPA/40 + Match/30 + Essay/15 + Test/15)
- [x] Admin Dashboard with 4 tabs: Pipeline, Reviews, Analytics, Audit Log
- [x] Analytics: program breakdown, GPA distribution, admission rates, avg processing time
- [x] Audit Log: full agent reasoning trail per application
- [x] Email & Calendar services (MOCKED per user request)
- [x] Comprehensive pytest test suite (18 tests, all passing)

## API Endpoints
- POST /api/applications - Submit application
- GET /api/applications/{thread_id} - Get status
- GET /api/admin/applications - List all
- GET /api/admin/analytics - Analytics dashboard data
- GET /api/admin/audit-log - Audit trail
- GET /api/admin/pending-reviews - Pending human reviews
- POST /api/admin/review/{thread_id} - Submit review decision
- POST /api/documents/upload/{thread_id} - Upload document
- GET /api/documents/list/{thread_id} - List documents

## Remaining Backlog
### P1
- [ ] Load testing for 100+ concurrent applications
- [ ] Playwright frontend E2E tests

### P2
- [ ] Containerization (docker-compose.yml, CI/CD)
- [ ] RAG-based FAQ chatbot for applicants
- [ ] Adaptive interview scheduling
- [ ] Admin bias detection dashboard
- [ ] Architectural documentation, README, Swagger specs
