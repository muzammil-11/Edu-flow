from datetime import datetime, timedelta
import uuid

class CalendarService:
    """Mock Google Calendar service that logs to console."""
    
    def __init__(self):
        self.events = []
    
    async def schedule_interview(self, applicant_email: str, applicant_name: str, interview_date: str = None):
        """Schedule an interview (mock)."""
        if not interview_date:
            # Default to 7 days from now at 10 AM
            interview_datetime = datetime.utcnow() + timedelta(days=7)
            interview_datetime = interview_datetime.replace(hour=10, minute=0, second=0, microsecond=0)
            interview_date = interview_datetime.isoformat()
        
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "summary": f"Interview: {applicant_name}",
            "description": f"Admission interview with {applicant_name}",
            "start": interview_date,
            "end": (datetime.fromisoformat(interview_date) + timedelta(minutes=30)).isoformat(),
            "attendees": [applicant_email, "admissions@eduflow.edu"],
            "location": "Virtual (Zoom link will be provided)"
        }
        
        self.events.append(event)
        
        # Mock: Log to console
        print("="*60)
        print("📅 CALENDAR EVENT CREATED (MOCK)")
        print("="*60)
        print(f"Event ID: {event_id}")
        print(f"Title: {event['summary']}")
        print(f"Date: {interview_date}")
        print(f"Duration: 30 minutes")
        print(f"Attendees: {', '.join(event['attendees'])}")
        print(f"Location: {event['location']}")
        print("="*60)
        
        return {
            "status": "scheduled",
            "event_id": event_id,
            "interview_date": interview_date,
            "calendar_link": f"https://calendar.google.com/calendar/event?eid={event_id}"
        }
    
    async def cancel_interview(self, event_id: str):
        """Cancel an interview (mock)."""
        print(f"📅 CALENDAR EVENT CANCELLED (MOCK): {event_id}")
        self.events = [e for e in self.events if e["id"] != event_id]
        return {"status": "cancelled"}
    
    async def reschedule_interview(self, event_id: str, new_date: str):
        """Reschedule an interview (mock)."""
        for event in self.events:
            if event["id"] == event_id:
                event["start"] = new_date
                event["end"] = (datetime.fromisoformat(new_date) + timedelta(minutes=30)).isoformat()
                print(f"📅 INTERVIEW RESCHEDULED (MOCK): {event_id} to {new_date}")
                return {"status": "rescheduled", "new_date": new_date}
        return {"status": "not_found"}

# Singleton instance
calendar_service = CalendarService()