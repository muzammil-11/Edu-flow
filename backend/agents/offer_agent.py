from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.email_service import email_service
import asyncio

async def offer_dispatch_node_async(state: dict) -> dict:
    """Dispatch offer to successful applicants asynchronously."""
    final_decision = state.get("final_decision")
    submitted_data = state.get("submitted_data", {})
    
    offer_extended = final_decision == "admitted"
    offer_details = None
    offer_expiration = None
    
    if offer_extended:
        offer_expiration = (datetime.utcnow() + timedelta(days=30)).isoformat()
        offer_details = {
            "program": submitted_data.get("program"),
            "start_date": "Fall 2026",
            "scholarship": "Merit-based available",
            "expiration": offer_expiration
        }
    
    # Send email notification
    await email_service.send_offer_letter(
        recipient_email=submitted_data.get('email'),
        name=submitted_data.get('name'),
        program=submitted_data.get('program'),
        decision=final_decision
    )
    
    return {
        "current_stage": "completed",
        "status": "completed",
        "offer_extended": offer_extended,
        "offer_details": offer_details,
        "offer_expiration": offer_expiration,
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Offer: {'Admission offer sent' if offer_extended else 'Decision notification sent'} to {submitted_data.get('email')}"
        ]
    }

def offer_dispatch_node(state: dict) -> dict:
    """Dispatch offer to successful applicants."""
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, offer_dispatch_node_async(state))
            return future.result(timeout=30)
    except Exception as e:
        print(f"Offer dispatch error: {e}")
        final_decision = state.get("final_decision")
        submitted_data = state.get("submitted_data", {})
        offer_extended = final_decision == "admitted"
        return {
            "current_stage": "completed",
            "status": "completed",
            "offer_extended": offer_extended,
            "offer_details": None,
            "offer_expiration": None,
            "agent_reasoning": state.get("agent_reasoning", []) + [
                f"Offer: Decision sent to {submitted_data.get('email')}"
            ]
        }