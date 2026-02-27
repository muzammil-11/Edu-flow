from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ApplicationState(TypedDict):
    """State schema for the multi-agent application workflow."""
    # Input data
    application_id: str
    user_id: str
    submitted_data: dict
    
    # Messages and communication
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Application tracking
    current_stage: str
    status: str
    
    # Verification data
    documents_verified: bool
    document_issues: list[str]
    missing_documents: list[str]
    
    # Eligibility assessment
    eligibility_score: float
    eligibility_reasons: list[str]
    meets_basic_requirements: bool
    
    # Interview scheduling
    interview_scheduled: bool
    interview_date: Optional[str]
    interview_notes: Optional[str]
    
    # Decision information
    final_decision: Optional[str]
    decision_reasoning: Optional[str]
    decision_timestamp: Optional[str]
    
    # Offer details
    offer_extended: bool
    offer_details: Optional[dict]
    offer_expiration: Optional[str]
    
    # Human-in-the-loop tracking
    requires_human_review: bool
    human_review_reason: Optional[str]
    human_approval: Optional[bool]
    
    # Metadata
    created_at: str
    updated_at: str
    agent_reasoning: list[str]