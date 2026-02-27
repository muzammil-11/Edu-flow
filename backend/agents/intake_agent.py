from emergentintegrations.llm.chat import LlmChat, UserMessage
import os

def create_intake_agent():
    """Create the application intake agent."""
    api_key = os.getenv("EMERGENT_LLM_KEY")
    chat = LlmChat(
        api_key=api_key,
        session_id="intake-agent",
        system_message="""You are the Application Intake Agent for university admissions. Your responsibility is to:
    1. Extract structured data from user submissions
    2. Validate that all required fields are present
    3. Normalize data formats (dates, phone numbers, etc.)
    4. Flag any obvious data quality issues
    
    Respond concisely confirming data has been received and validated."""
    ).with_model("openai", "gpt-4o")
    return chat

async def intake_node_async(state: dict) -> dict:
    """Process application intake asynchronously."""
    submitted_data = state.get("submitted_data", {})
    
    intake_message = f"""New application received:
Name: {submitted_data.get('name')}
Email: {submitted_data.get('email')}
Phone: {submitted_data.get('phone')}
Program: {submitted_data.get('program')}
GPA: {submitted_data.get('gpa')}

Validate this information and confirm receipt."""
    
    try:
        chat = create_intake_agent()
        response = await chat.send_message(UserMessage(text=intake_message))
        response_text = response
    except Exception as e:
        print(f"Intake agent error: {e}")
        response_text = f"Intake processed: Application for {submitted_data.get('name')} received successfully."
    
    return {
        "current_stage": "verification",
        "status": "in_progress",
        "agent_reasoning": state.get("agent_reasoning", []) + [
            f"Intake: Received application for {submitted_data.get('name')} - {submitted_data.get('program')}"
        ]
    }

def intake_node(state: dict) -> dict:
    """Synchronous wrapper for intake node."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, intake_node_async(state))
                return future.result(timeout=30)
        else:
            return asyncio.run(intake_node_async(state))
    except Exception as e:
        print(f"Intake node error: {e}")
        submitted_data = state.get("submitted_data", {})
        return {
            "current_stage": "verification",
            "status": "in_progress",
            "agent_reasoning": state.get("agent_reasoning", []) + [
                f"Intake: Received application for {submitted_data.get('name')} - {submitted_data.get('program')}"
            ]
        }