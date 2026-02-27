from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
import os
import asyncio

def create_decision_agent():
    """Create the decision agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    chat = LlmChat(
        api_key=api_key,
        session_id="decision-agent",
        system_message="""You are the Decision Agent. Make final admission decisions based on:
    1. Eligibility assessment
    2. Document verification status
    3. Interview (if conducted)
    
    Provide decision: Admitted, Waitlisted, or Denied with clear reasoning."""
    ).with_model("openai", "gpt-4o")
    return chat

def decision_node(state: dict) -> dict:
    """Make final decision on application."""
    submitted_data = state.get("submitted_data", {})
    meets_requirements = state.get("meets_basic_requirements", False)
    eligibility_score = state.get("eligibility_score", 0)
    
    decision_message = f"""Make admission decision for:
Name: {submitted_data.get('name')}
Program: {submitted_data.get('program')}
Eligibility Score: {eligibility_score}/100
Meets Requirements: {meets_requirements}
Interview Completed: {state.get('interview_scheduled', False)}

Provide final decision with reasoning."""
    
    try:
        chat = create_decision_agent()
        response = asyncio.run(chat.send_message(UserMessage(text=decision_message)))
    except Exception as e:
        pass
    
    # Determine decision
    if meets_requirements and eligibility_score >= 75:
        decision = "admitted"
    elif meets_requirements and eligibility_score >= 60:
        decision = "waitlisted"
    else:
        decision = "denied"
    
    reasoning = f"Decision based on eligibility score of {eligibility_score:.1f}/100"
    
    return {
        "current_stage": "dispatch",
        "final_decision": decision,
        "decision_reasoning": reasoning,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Decision: Application {decision.upper()}"
        ]
    }