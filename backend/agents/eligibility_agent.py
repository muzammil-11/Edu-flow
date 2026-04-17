"""
Eligibility Screening Agent with FAISS Vector DB integration.
Uses vector similarity matching + rule-based scoring for comprehensive eligibility assessment.
"""
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.vector_store import vector_store


def create_eligibility_agent():
    """Create the eligibility screening agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    chat = LlmChat(
        api_key=api_key,
        session_id="eligibility-agent",
        system_message="""You are the Eligibility Screening Agent. You evaluate applicants using:
    1. FAISS vector similarity scores (profile-program matching)
    2. GPA and program-specific requirements
    3. Test scores and essay quality
    
    You receive structured eligibility data from the vector database.
    Provide a clear summary recommendation: Eligible, Not Eligible, or Requires Review.
    Keep your response concise.""",
    ).with_model("openai", "gpt-4o")
    return chat


async def eligibility_node_async(state: dict) -> dict:
    """Screen for eligibility using FAISS vector matching + rules."""
    submitted_data = state.get("submitted_data", {})
    gpa = float(submitted_data.get("gpa", 0))

    # Use FAISS vector store for comprehensive eligibility scoring
    eligibility_result = vector_store.compute_eligibility_score(submitted_data)

    score = eligibility_result["score"]
    reasons = eligibility_result["reasons"]
    meets_requirements = eligibility_result["meets_requirements"]
    requires_review = eligibility_result["requires_review"]
    review_reason = eligibility_result["review_reason"]
    matches = eligibility_result["matches"]

    # Build LLM prompt with vector DB results
    match_info = "\n".join(
        f"  - {m['program']}: similarity={m['similarity_score']:.3f}"
        for m in matches
    )

    eligibility_message = f"""Evaluate eligibility for:
Name: {submitted_data.get('name')}
Program: {submitted_data.get('program')}
GPA: {gpa}
Test Scores: {submitted_data.get('test_scores', 'N/A')}

FAISS Vector Matching Results:
{match_info}

Scoring Breakdown:
  GPA Score: {eligibility_result['gpa_score']}/40
  Similarity Score: {eligibility_result['similarity_score']}/30
  Essay Score: {eligibility_result['essay_score']}/15
  Test Score: {eligibility_result['test_score']}/15
  Total: {score}/100

Meets Requirements: {meets_requirements}
Requires Review: {requires_review}

Provide a brief assessment."""

    try:
        chat = create_eligibility_agent()
        response = await chat.send_message(UserMessage(text=eligibility_message))
    except Exception as e:
        print(f"Eligibility agent error: {e}")

    # Determine next stage
    if requires_review:
        next_stage = "interview" if meets_requirements else "decision"
    else:
        next_stage = "interview" if meets_requirements else "decision"

    # Build reasoning
    reasoning_parts = [
        f"Eligibility: {'Eligible' if meets_requirements else 'Not Eligible'} - Score: {score}/100",
        f"(GPA: {eligibility_result['gpa_score']}/40, Match: {eligibility_result['similarity_score']}/30, Essay: {eligibility_result['essay_score']}/15, Test: {eligibility_result['test_score']}/15)",
    ]
    if requires_review:
        reasoning_parts.append(f"[REQUIRES REVIEW: {review_reason}]")

    return {
        "current_stage": next_stage,
        "meets_basic_requirements": meets_requirements,
        "eligibility_score": score,
        "eligibility_reasons": reasons,
        "requires_human_review": requires_review,
        "human_review_reason": review_reason,
        "agent_reasoning": state.get("agent_reasoning", [])
        + [" ".join(reasoning_parts)],
    }


def eligibility_node(state: dict) -> dict:
    """Synchronous wrapper for eligibility node."""
    import asyncio

    try:
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, eligibility_node_async(state))
            return future.result(timeout=30)
    except Exception as e:
        print(f"Eligibility node error: {e}")
        # Fallback to basic vector store scoring without LLM
        submitted_data = state.get("submitted_data", {})
        try:
            result = vector_store.compute_eligibility_score(submitted_data)
            return {
                "current_stage": "interview" if result["meets_requirements"] else "decision",
                "meets_basic_requirements": result["meets_requirements"],
                "eligibility_score": result["score"],
                "eligibility_reasons": result["reasons"],
                "requires_human_review": result["requires_review"],
                "human_review_reason": result["review_reason"],
                "agent_reasoning": state.get("agent_reasoning", [])
                + [f"Eligibility: Score {result['score']}/100 (FAISS fallback)"],
            }
        except Exception as fallback_err:
            print(f"Eligibility fallback error: {fallback_err}")
            gpa = float(submitted_data.get("gpa", 0))
            meets = gpa >= 3.0
            score = min(gpa * 25, 100) if meets else gpa * 20
            return {
                "current_stage": "interview" if meets else "decision",
                "meets_basic_requirements": meets,
                "eligibility_score": score,
                "eligibility_reasons": [f"GPA of {gpa}"],
                "requires_human_review": False,
                "human_review_reason": None,
                "agent_reasoning": state.get("agent_reasoning", [])
                + [f"Eligibility: Score {score:.1f}/100 (basic fallback)"],
            }
