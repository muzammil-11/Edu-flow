from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
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
        
        # Execute workflow asynchronously
        graph = await orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run graph in background
        import asyncio
        async def run_workflow():
            try:
                result = await graph.ainvoke(initial_state, config)
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
            except Exception as e:
                print(f"Workflow error: {e}")
        
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
        graph = await orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph.aget_state(config)
        
        return ApplicationStatusResponse(
            thread_id=thread_id,
            application_id=application.get("_id"),
            current_stage=state.values.get("current_stage", "unknown") if state else "unknown",
            status=state.values.get("status", "unknown") if state else "unknown",
            agent_reasoning=state.values.get("agent_reasoning", []) if state else [],
            final_decision=state.values.get("final_decision") if state else None,
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
        graph = await orchestrator.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        state = await graph.aget_state(config)
        
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