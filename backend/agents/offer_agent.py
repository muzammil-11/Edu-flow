from datetime import datetime, timedelta

def offer_dispatch_node(state: dict) -> dict:
    """Dispatch offer to successful applicants."""
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