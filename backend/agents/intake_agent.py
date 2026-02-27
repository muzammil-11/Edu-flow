from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
import json
import os

@tool
def parse_application_submission(raw_submission: str) -> dict:
    """Parse and validate raw application submission data."""
    return {
        "raw_data": raw_submission,
        "validation_status": "received"
    }

def create_intake_agent():
    """Create the application intake agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        base_url="https://inference.emergentagi.com/v1",
        temperature=0
    )
    
    system_prompt = """You are the Application Intake Agent for university admissions. Your responsibility is to:
    1. Extract structured data from user submissions
    2. Validate that all required fields are present
    3. Normalize data formats (dates, phone numbers, etc.)
    4. Flag any obvious data quality issues
    
    Respond concisely confirming data has been received and validated."""
    
    return llm, system_prompt

def intake_node(state: dict) -> dict:
    """Process application intake."""
    llm, system_prompt = create_intake_agent()
    
    messages = state.get("messages", [])
    submitted_data = state.get("submitted_data", {})
    
    # Create intake message
    intake_message = f"""{system_prompt}
    
    New application received:
    Name: {submitted_data.get('name')}
    Email: {submitted_data.get('email')}
    Phone: {submitted_data.get('phone')}
    Program: {submitted_data.get('program')}
    GPA: {submitted_data.get('gpa')}
    
    Validate this information and confirm receipt."""
    
    response = llm.invoke(intake_message)
    
    return {
        "messages": messages + [AIMessage(content=response.content)],
        "current_stage": "verification",
        "status": "in_progress",
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Intake: Received application for {submitted_data.get('name')} - {submitted_data.get('program')}"
        ]
    }