from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
import os

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

async def decision_node_async(state: dict) -> dict:
    """Make final decision on application asynchronously."""
    submitted_data = state.get("submitted_data", {})
    meets_requirements = state.get("meets_basic_requirements", False)
    eligibility_score = state.get("eligibility_score", 0)
    requires_review = state.get("requires_human_review", False)
    
    decision_message = f"""Make admission decision for:
Name: {submitted_data.get('name')}
Program: {submitted_data.get('program')}
Eligibility Score: {eligibility_score}/100
Meets Requirements: {meets_requirements}
Interview Completed: {state.get('interview_scheduled', False)}
Requires Human Review: {requires_review}

Provide final decision with reasoning."""
    
    try:
        chat = create_decision_agent()
        response = await chat.send_message(UserMessage(text=decision_message))
    except Exception as e:
        print(f"Decision agent error: {e}")
    
    # Determine decision
    if requires_review:
        decision = "waitlisted"  # Send to waitlist for human review
    elif meets_requirements and eligibility_score >= 75:
        decision = "admitted"
    elif meets_requirements and eligibility_score >= 60:
        decision = "waitlisted"
    else:
        decision = "denied"
    
    reasoning = f"Decision based on eligibility score of {eligibility_score:.1f}/100"
    if requires_review:
        reasoning += " - Flagged for human review due to borderline qualifications"
    
    return {
        "current_stage": "dispatch",
        "final_decision": decision,
        "decision_reasoning": reasoning,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Decision: Application {decision.upper()}"
        ]
    }

def decision_node(state: dict) -> dict:
    """Synchronous wrapper for decision node."""
    import asyncio
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, decision_node_async(state))
            return future.result(timeout=30)
    except Exception as e:
        print(f"Decision node error: {e}")
        submitted_data = state.get("submitted_data", {})
        meets_requirements = state.get("meets_basic_requirements", False)
        eligibility_score = state.get("eligibility_score", 0)
        decision = "admitted" if meets_requirements and eligibility_score >= 75 else "waitlisted" if meets_requirements else "denied"
        return {
            "current_stage": "dispatch",
            "final_decision": decision,
            "decision_reasoning": f"Decision based on eligibility score of {eligibility_score:.1f}/100",
            "decision_timestamp": datetime.utcnow().isoformat(),
            "agent_reasoning": state.get("agent_reasoning", []) + [
                f"Decision: Application {decision.upper()}"
            ]
        }