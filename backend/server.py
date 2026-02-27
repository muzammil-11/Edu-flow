from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from db_config import DatabaseConfig
from graph_builder import MultiAgentOrchestrator
from dotenv import load_dotenv
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    print("Starting up application...")
    # Initialize database connection
    await DatabaseConfig.get_database()
    yield
    print("Shutting down application...")
    await DatabaseConfig.close()

app = FastAPI(title="University Admission Workflow System", lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    os.getenv("CORS_ORIGINS", "*"),
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ApplicationSubmissionRequest(BaseModel):
    name: str
    email: str
    phone: str
    program: str
    gpa: float
    test_scores: Optional[str] = None
    essay: Optional[str] = None

class ApplicationResponse(BaseModel):
    application_id: str
    thread_id: str
    status: str
    message: str

class ApplicationStatusResponse(BaseModel):
    thread_id: str
    application_id: str
    current_stage: str
    status: str
    agent_reasoning: List[str]
    final_decision: Optional[str] = None
    updated_at: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, thread_id: str, websocket: WebSocket):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)
    
    async def disconnect(self, thread_id: str, websocket: WebSocket):
        if thread_id in self.active_connections:
            self.active_connections[thread_id].remove(websocket)
            if not self.active_connections[thread_id]:
                del self.active_connections[thread_id]
    
    async def broadcast(self, thread_id: str, message: dict):
        if thread_id in self.active_connections:
            for connection in self.active_connections[thread_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()
orchestrator = MultiAgentOrchestrator()

# API Endpoints
@app.get("/api/")
async def root():
    return {"message": "University Admission Workflow System API"}

@app.post("/api/applications", response_model=ApplicationResponse)
async def submit_application(request: ApplicationSubmissionRequest):
    """Submit a new application and initiate the workflow."""
    try:
        # Create unique identifiers
        application_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())
        
        # Initialize application state
        initial_state = {
            "application_id": application_id,
            "user_id": request.email,
            "submitted_data": request.dict(),
            "messages": [],
            "current_stage": "intake",
            "status": "pending",
            "documents_verified": False,
            "document_issues": [],
            "missing_documents": [],
            "eligibility_score": 0,
            "eligibility_reasons": [],
            "meets_basic_requirements": False,
            "interview_scheduled": False,
            "interview_date": None,
            "interview_notes": None,
            "final_decision": None,
            "decision_reasoning": None,
            "decision_timestamp": None,
            "offer_extended": False,
            "offer_details": None,
            "offer_expiration": None,
            "requires_human_review": False,
            "human_review_reason": None,
            "human_approval": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "agent_reasoning": []
        }
        
        # Store application metadata
        db = await DatabaseConfig.get_database()
        await db.applications.insert_one({
            "_id": application_id,
            "thread_id": thread_id,
            "user_email": request.email,
            "submitted_data": request.dict(),
            "created_at": datetime.now(timezone.utc),
            "current_stage": "intake",
            "status": "pending"
        })
        
        # Execute workflow in background thread to avoid event loop issues
        graph = orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run graph in background using thread executor
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        async def run_workflow():
            try:
                # Run graph.invoke in a separate thread to avoid event loop conflicts
                loop = asyncio.get_event_loop()
                executor = ThreadPoolExecutor(max_workers=1)
                result = await loop.run_in_executor(executor, graph.invoke, initial_state, config)
                
                # Update database with final state
                await db.applications.update_one(
                    {"_id": application_id},
                    {"$set": {
                        "current_stage": result.get("current_stage"),
                        "status": result.get("status"),
                        "final_decision": result.get("final_decision"),
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                
                # Broadcast final state via WebSocket
                await manager.broadcast(thread_id, {
                    "type": "workflow_complete",
                    "data": {
                        "current_stage": result.get("current_stage"),
                        "status": result.get("status"),
                        "final_decision": result.get("final_decision"),
                        "agent_reasoning": result.get("agent_reasoning", [])
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                print(f"Workflow completed for {thread_id}: {result.get('final_decision')}")
            except Exception as e:
                print(f"Workflow error for {thread_id}: {e}")
                import traceback
                traceback.print_exc()
        
        asyncio.create_task(run_workflow())
        
        return ApplicationResponse(
            application_id=application_id,
            thread_id=thread_id,
            status="submitted",
            message="Application submitted successfully. Processing has begun."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")

@app.get("/api/applications/{thread_id}", response_model=ApplicationStatusResponse)
async def get_application_status(thread_id: str):
    """Get the current status of an application."""
    try:
        db = await DatabaseConfig.get_database()
        application = await db.applications.find_one({"thread_id": thread_id})
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get current state from checkpointer
        graph = orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        
        return ApplicationStatusResponse(
            thread_id=thread_id,
            application_id=application.get("_id"),
            current_stage=state.values.get("current_stage", "unknown") if state and state.values else "unknown",
            status=state.values.get("status", "unknown") if state and state.values else "unknown",
            agent_reasoning=state.values.get("agent_reasoning", []) if state and state.values else [],
            final_decision=state.values.get("final_decision") if state and state.values else None,
            updated_at=datetime.now(timezone.utc).isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application status: {str(e)}")

@app.get("/api/admin/applications")
async def list_all_applications():
    """Get all applications for admin dashboard."""
    try:
        db = await DatabaseConfig.get_database()
        applications = await db.applications.find({}, {"_id": 0}).to_list(100)
        
        return {"applications": applications, "total": len(applications)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list applications: {str(e)}")

@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """WebSocket endpoint for real-time application status updates."""
    await manager.connect(thread_id, websocket)
    
    try:
        # Send initial state
        graph = orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        state = graph.get_state(config)
        
        if state and state.values:
            await websocket.send_json({
                "type": "state_update",
                "data": {
                    "current_stage": state.values.get("current_stage"),
                    "status": state.values.get("status"),
                    "agent_reasoning": state.values.get("agent_reasoning", [])
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_json()
                # Handle incoming messages if needed
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        await manager.disconnect(thread_id, websocket)
    except Exception as e:
        await manager.disconnect(thread_id, websocket)
        print(f"WebSocket error: {e}")

# Document Upload Endpoints
@app.post("/api/documents/upload/{thread_id}")
async def upload_document(thread_id: str, file: UploadFile = File(...), document_type: str = "transcript"):
    """Upload a document for an application."""
    try:
        # Read file content
        content = await file.read()
        
        # Extract text using OCR/PDF parsing
        extracted_text = ""
        if file.content_type == "application/pdf":
            try:
                from pypdf import PdfReader
                from io import BytesIO
                pdf_reader = PdfReader(BytesIO(content))
                extracted_text = ""
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PDF extraction error: {e}")
        elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
            try:
                import pytesseract
                from PIL import Image
                from io import BytesIO
                image = Image.open(BytesIO(content))
                extracted_text = pytesseract.image_to_string(image)
            except Exception as e:
                print(f"OCR error: {e}")
                extracted_text = "[OCR not available]"
        
        # Store document in MongoDB
        db = await DatabaseConfig.get_database()
        document_id = str(uuid.uuid4())
        await db.documents.insert_one({
            "_id": document_id,
            "thread_id": thread_id,
            "document_type": document_type,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "extracted_text": extracted_text[:5000],  # Store first 5000 chars
            "uploaded_at": datetime.now(timezone.utc),
            "verified": False
        })
        
        return {
            "document_id": document_id,
            "status": "uploaded",
            "extracted_text_preview": extracted_text[:500] if extracted_text else None,
            "message": "Document uploaded and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@app.get("/api/documents/list/{thread_id}")
async def list_documents(thread_id: str):
    """List all documents for an application."""
    try:
        db = await DatabaseConfig.get_database()
        documents = await db.documents.find({"thread_id": thread_id}, {"_id": 0}).to_list(None)
        
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# Human-in-the-Loop Approval Endpoints
@app.get("/api/admin/pending-reviews")
async def get_pending_reviews():
    """Get applications requiring human review."""
    try:
        db = await DatabaseConfig.get_database()
        # Find applications in the database
        applications = await db.applications.find({}, {"_id": 0}).to_list(100)
        
        # Check which ones need review from their states
        pending_reviews = []
        graph = orchestrator.get_compiled_graph()
        
        for app in applications:
            thread_id = app.get("thread_id")
            config = {"configurable": {"thread_id": thread_id}}
            state = graph.get_state(config)
            
            if state and state.values:
                requires_review = state.values.get("requires_human_review", False)
                if requires_review and state.values.get("current_stage") not in ["completed"]:
                    pending_reviews.append({
                        "thread_id": thread_id,
                        "application_id": app.get("_id"),
                        "applicant_name": app.get("submitted_data", {}).get("name"),
                        "applicant_email": app.get("user_email"),
                        "program": app.get("submitted_data", {}).get("program"),
                        "gpa": app.get("submitted_data", {}).get("gpa"),
                        "current_stage": state.values.get("current_stage"),
                        "review_reason": state.values.get("human_review_reason"),
                        "eligibility_score": state.values.get("eligibility_score"),
                        "submitted_at": app.get("created_at")
                    })
        
        return {"pending_reviews": pending_reviews, "total": len(pending_reviews)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending reviews: {str(e)}")

class ReviewDecision(BaseModel):
    approved: bool
    comments: Optional[str] = None

@app.post("/api/admin/review/{thread_id}")
async def submit_review_decision(thread_id: str, decision: ReviewDecision):
    """Submit human review decision for an application."""
    try:
        db = await DatabaseConfig.get_database()
        
        # Get current state
        graph = orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update state with human approval
        current_values = dict(state.values)
        current_values["human_approval"] = decision.approved
        current_values["requires_human_review"] = False
        current_values["agent_reasoning"] = current_values.get("agent_reasoning", []) + [
            f"Human Review: {'APPROVED' if decision.approved else 'REJECTED'} - {decision.comments or 'No comments'}"
        ]
        
        # If approved, adjust the decision
        if decision.approved:
            if current_values.get("eligibility_score", 0) >= 60:
                current_values["final_decision"] = "admitted"
            else:
                current_values["final_decision"] = "waitlisted"
        else:
            current_values["final_decision"] = "denied"
        
        # Continue the workflow by updating to dispatch stage
        current_values["current_stage"] = "dispatch"
        
        # Update graph state (this will trigger the dispatch node)
        graph.update_state(config, current_values)
        
        # Update database
        await db.applications.update_one(
            {"thread_id": thread_id},
            {"$set": {
                "human_review_completed": True,
                "human_decision": decision.approved,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "status": "success",
            "message": f"Review decision recorded: {'Approved' if decision.approved else 'Rejected'}",
            "final_decision": current_values["final_decision"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit review: {str(e)}")