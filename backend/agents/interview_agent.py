from datetime import datetime, timedelta

def interview_scheduler_node(state: dict) -> dict:
    """Schedule interview with applicant."""
    submitted_data = state.get("submitted_data", {})
    
    # Schedule interview 7 days from now
    interview_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    
    return {
        "current_stage": "decision",
        "interview_scheduled": True,
        "interview_date": interview_date,
        "interview_notes": f"Interview scheduled via email to {submitted_data.get('email')}",
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Interview: Scheduled for {interview_date[:10]}"
        ]
    }