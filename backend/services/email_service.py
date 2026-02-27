from datetime import datetime
import os

class EmailService:
    """Mock email service that logs to console."""
    
    def __init__(self):
        self.emails_sent = []
    
    async def send_offer_letter(self, recipient_email: str, name: str, program: str, decision: str):
        """Send offer letter email (mock)."""
        email_content = self._generate_offer_email(name, program, decision)
        
        # Mock: Log to console instead of sending
        print("="*60)
        print("📧 EMAIL SENT (MOCK)")
        print("="*60)
        print(f"To: {recipient_email}")
        print(f"From: admissions@eduflow.edu")
        print(f"Subject: University Admission Decision - {program}")
        print(f"\n{email_content}")
        print("="*60)
        
        self.emails_sent.append({
            "to": recipient_email,
            "subject": f"University Admission Decision - {program}",
            "content": email_content,
            "sent_at": datetime.utcnow().isoformat()
        })
        
        return {"status": "sent", "message_id": f"mock-{len(self.emails_sent)}"}
    
    async def send_interview_invitation(self, recipient_email: str, name: str, interview_date: str):
        """Send interview invitation email (mock)."""
        email_content = f"""Dear {name},

Congratulations! We are pleased to invite you for an interview as part of your application review process.

Interview Details:
Date & Time: {interview_date}
Format: Virtual Interview
Duration: 30 minutes

A calendar invitation has been sent separately. Please confirm your attendance.

Best regards,
Admissions Office
EduFlow University
"""
        
        print("="*60)
        print("📧 INTERVIEW INVITATION SENT (MOCK)")
        print("="*60)
        print(f"To: {recipient_email}")
        print(f"Subject: Interview Invitation - EduFlow University")
        print(f"\n{email_content}")
        print("="*60)
        
        return {"status": "sent", "message_id": f"mock-interview-{len(self.emails_sent)}"}
    
    def _generate_offer_email(self, name: str, program: str, decision: str) -> str:
        """Generate offer letter email content."""
        if decision == "admitted":
            return f"""Dear {name},

Congratulations! We are delighted to inform you that you have been ADMITTED to the {program} program at EduFlow University for Fall 2026.

Your application demonstrated exceptional qualifications, and we are excited to welcome you to our community.

Next Steps:
1. Accept your offer by March 15, 2026
2. Complete enrollment paperwork
3. Attend orientation on August 20, 2026

Welcome to EduFlow University!

Best regards,
Admissions Office
EduFlow University
"""
        elif decision == "waitlisted":
            return f"""Dear {name},

Thank you for your application to the {program} program at EduFlow University.

After careful review, we have placed your application on our WAITLIST. This means you are a strong candidate, and we will notify you if a spot becomes available.

You will hear from us by April 15, 2026.

Best regards,
Admissions Office
EduFlow University
"""
        else:  # denied
            return f"""Dear {name},

Thank you for your interest in the {program} program at EduFlow University.

After careful consideration, we regret to inform you that we are unable to offer you admission at this time.

We encourage you to consider reapplying in the future and wish you success in your academic pursuits.

Best regards,
Admissions Office
EduFlow University
"""

# Singleton instance
email_service = EmailService()