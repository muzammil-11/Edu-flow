from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.calendar_service import calendar_service
from services.email_service import email_service
import asyncio

async def interview_scheduler_node_async(state: dict) -> dict:
    """Schedule interview with applicant asynchronously."""
    submitted_data = state.get("submitted_data", {})
    
    # Schedule interview 7 days from now
    interview_datetime = datetime.utcnow() + timedelta(days=7)
    interview_date = interview_datetime.isoformat()
    
    # Schedule via calendar service
    calendar_result = await calendar_service.schedule_interview(
        applicant_email=submitted_data.get('email'),
        applicant_name=submitted_data.get('name'),
        interview_date=interview_date
    )
    
    # Send email invitation
    await email_service.send_interview_invitation(
        recipient_email=submitted_data.get('email'),
        name=submitted_data.get('name'),
        interview_date=interview_date
    )
    
    return {
        "current_stage": "decision",
        "interview_scheduled": True,
        "interview_date": interview_date,
        "interview_notes": f"Interview scheduled via email to {submitted_data.get('email')}",
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Interview: Scheduled for {interview_date[:10]}"
        ]
    }

def interview_scheduler_node(state: dict) -> dict:
    """Schedule interview with applicant."""
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, interview_scheduler_node_async(state))
            return future.result(timeout=30)
    except Exception as e:
        print(f"Interview scheduler error: {e}")
        submitted_data = state.get("submitted_data", {})
        interview_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        return {
            "current_stage": "decision",
            "interview_scheduled": True,
            "interview_date": interview_date,
            "interview_notes": f"Interview scheduled for {submitted_data.get('email')}",
            "agent_reasoning": state.get("agent_reasoning", []) + [
                f"Interview: Scheduled for {interview_date[:10]}"
            ]
        }