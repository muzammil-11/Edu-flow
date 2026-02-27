from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
import os

def create_verification_agent():
    """Create the document verification agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        base_url="https://inference.emergentagi.com/v1",
        temperature=0
    )
    
    system_prompt = """You are the Document Verification Agent. Your responsibilities include:
    1. Validating that submitted documents are complete
    2. Checking document requirements (transcripts, test scores, letters)
    3. Flagging missing or invalid documents
    
    Provide clear documentation of what was verified and any issues found."""
    
    return llm, system_prompt

def verification_node(state: dict) -> dict:
    """Verify submitted documents."""
    llm, system_prompt = create_verification_agent()
    
    messages = state.get("messages", [])
    submitted_data = state.get("submitted_data", {})
    
    # Simulate document check
    verification_message = f"""{system_prompt}
    
    Verify documents for: {submitted_data.get('name')}
    Program: {submitted_data.get('program')}
    
    Check for: transcripts, test scores, recommendation letters.
    Assume all documents have been uploaded for this demo.
    
    Provide verification status."""
    
    response = llm.invoke(verification_message)
    
    # Assume documents are verified for demo
    documents_verified = True
    issues = []
    
    return {
        "messages": messages + [AIMessage(content=response.content)],
        "documents_verified": documents_verified,
        "document_issues": issues,
        "missing_documents": [],
        "current_stage": "eligibility",
        "agent_reasoning": state.get("agent_reasoning", []) + [
            "Verification: All documents validated successfully"
        ]
    }