from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import asyncio

def create_eligibility_agent():
    """Create the eligibility screening agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    chat = LlmChat(
        api_key=api_key,
        session_id="eligibility-agent",
        system_message="""You are the Eligibility Screening Agent. Evaluate applicants based on:
    1. GPA requirements (minimum 3.0)
    2. Program prerequisites
    3. Test scores
    
    Provide a clear recommendation: Eligible, Not Eligible, or Requires Review."""
    ).with_model("openai", "gpt-4o")
    return chat

def eligibility_node(state: dict) -> dict:
    """Screen for eligibility."""
    submitted_data = state.get("submitted_data", {})
    
    gpa = float(submitted_data.get('gpa', 0))
    
    eligibility_message = f"""Evaluate eligibility for:
Name: {submitted_data.get('name')}
Program: {submitted_data.get('program')}
GPA: {gpa}

Determine if applicant meets basic requirements."""
    
    try:
        chat = create_eligibility_agent()
        response = asyncio.run(chat.send_message(UserMessage(text=eligibility_message)))
    except Exception as e:
        pass
    
    # Calculate eligibility
    meets_requirements = gpa >= 3.0
    eligibility_score = min(gpa * 25, 100) if gpa >= 3.0 else gpa * 20
    reasons = []
    
    if meets_requirements:
        reasons.append(f"GPA of {gpa} meets minimum requirement of 3.0")
    else:
        reasons.append(f"GPA of {gpa} below minimum requirement of 3.0")
    
    return {
        "current_stage": "interview" if meets_requirements else "decision",
        "meets_basic_requirements": meets_requirements,
        "eligibility_score": eligibility_score,
        "eligibility_reasons": reasons,
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Eligibility: {'Eligible' if meets_requirements else 'Not Eligible'} - Score: {eligibility_score:.1f}/100"
        ]
    }