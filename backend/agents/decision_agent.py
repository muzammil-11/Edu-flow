from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from datetime import datetime
import os

def create_decision_agent():
    """Create the decision agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        base_url="https://inference.emergentagi.com/v1",
        temperature=0
    )
    
    system_prompt = """You are the Decision Agent. Make final admission decisions based on:
    1. Eligibility assessment
    2. Document verification status
    3. Interview (if conducted)
    
    Provide decision: Admitted, Waitlisted, or Denied with clear reasoning."""
    
    return llm, system_prompt

def decision_node(state: dict) -> dict:
    """Make final decision on application."""
    llm, system_prompt = create_decision_agent()
    
    messages = state.get("messages", [])
    submitted_data = state.get("submitted_data", {})
    meets_requirements = state.get("meets_basic_requirements", False)
    eligibility_score = state.get("eligibility_score", 0)
    
    decision_message = f"""{system_prompt}
    
    Make admission decision for:
    Name: {submitted_data.get('name')}
    Program: {submitted_data.get('program')}
    Eligibility Score: {eligibility_score}/100
    Meets Requirements: {meets_requirements}
    Interview Completed: {state.get('interview_scheduled', False)}
    
    Provide final decision with reasoning."""
    
    response = llm.invoke(decision_message)
    
    # Determine decision
    if meets_requirements and eligibility_score >= 75:
        decision = "admitted"
    elif meets_requirements and eligibility_score >= 60:
        decision = "waitlisted"
    else:
        decision = "denied"
    
    reasoning = f"Decision based on eligibility score of {eligibility_score:.1f}/100"
    
    return {
        "messages": messages + [AIMessage(content=response.content)],
        "current_stage": "dispatch",
        "final_decision": decision,
        "decision_reasoning": reasoning,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Decision: Application {decision.upper()}"
        ]
    }