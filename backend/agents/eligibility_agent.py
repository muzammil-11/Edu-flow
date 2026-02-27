from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
import os

def create_eligibility_agent():
    """Create the eligibility screening agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        base_url="https://inference.emergentagi.com/v1",
        temperature=0
    )
    
    system_prompt = """You are the Eligibility Screening Agent. Evaluate applicants based on:
    1. GPA requirements (minimum 3.0)
    2. Program prerequisites
    3. Test scores
    
    Provide a clear recommendation: Eligible, Not Eligible, or Requires Review."""
    
    return llm, system_prompt

def eligibility_node(state: dict) -> dict:
    """Screen for eligibility."""
    llm, system_prompt = create_eligibility_agent()
    
    messages = state.get("messages", [])
    submitted_data = state.get("submitted_data", {})
    
    gpa = float(submitted_data.get('gpa', 0))
    
    eligibility_message = f"""{system_prompt}
    
    Evaluate eligibility for:
    Name: {submitted_data.get('name')}
    Program: {submitted_data.get('program')}
    GPA: {gpa}
    
    Determine if applicant meets basic requirements."""
    
    response = llm.invoke(eligibility_message)
    
    # Calculate eligibility
    meets_requirements = gpa >= 3.0
    eligibility_score = min(gpa * 25, 100) if gpa >= 3.0 else gpa * 20
    reasons = []
    
    if meets_requirements:
        reasons.append(f"GPA of {gpa} meets minimum requirement of 3.0")
    else:
        reasons.append(f"GPA of {gpa} below minimum requirement of 3.0")
    
    return {
        "messages": messages + [AIMessage(content=response.content)],
        "current_stage": "interview" if meets_requirements else "decision",
        "meets_basic_requirements": meets_requirements,
        "eligibility_score": eligibility_score,
        "eligibility_reasons": reasons,
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Eligibility: {'Eligible' if meets_requirements else 'Not Eligible'} - Score: {eligibility_score:.1f}/100"
        ]
    }