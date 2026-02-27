from langgraph.graph import StateGraph, START, END
from typing import Literal
from state_schema import ApplicationState
from agents.intake_agent import intake_node
from agents.verification_agent import verification_node
from agents.eligibility_agent import eligibility_node
from agents.interview_agent import interview_scheduler_node
from agents.decision_agent import decision_node
from agents.offer_agent import offer_dispatch_node
from db_config import DatabaseConfig

class MultiAgentOrchestrator:
    """Orchestrates the multi-agent application workflow."""
    
    def __init__(self):
        self.graph = None
    
    def _build_graph(self):
        """Construct the LangGraph workflow."""
        workflow = StateGraph(ApplicationState)
        
        def route_after_eligibility(state: dict) -> Literal["interview", "decision", "human_review"]:
            """Route based on eligibility determination."""
            # Check if human review is required first
            if state.get("requires_human_review", False):
                return "human_review"
            # Otherwise route based on eligibility
            return "interview" if state.get("meets_basic_requirements") else "decision"
        
        def human_review_node(state: dict) -> dict:
            """Pause workflow for human review."""
            return {
                "current_stage": "human_review",
                "status": "pending_review",
                "agent_reasoning": state.get("agent_reasoning", []) + [
                    "Human Review: Application flagged for manual review - workflow paused"
                ]
            }
        
        # Add nodes to graph
        workflow.add_node("intake", intake_node)
        workflow.add_node("verification", verification_node)
        workflow.add_node("eligibility", eligibility_node)
        workflow.add_node("human_review", human_review_node)
        workflow.add_node("interview", interview_scheduler_node)
        workflow.add_node("decision", decision_node)
        workflow.add_node("dispatch", offer_dispatch_node)
        
        # Add edges
        workflow.add_edge(START, "intake")
        workflow.add_edge("intake", "verification")
        workflow.add_edge("verification", "eligibility")
        workflow.add_conditional_edges(
            "eligibility",
            route_after_eligibility,
            {"interview": "interview", "decision": "decision", "human_review": "human_review"}
        )
        # Human review node ends the workflow - admin must resume it
        workflow.add_edge("human_review", END)
        workflow.add_edge("interview", "decision")
        workflow.add_edge("decision", "dispatch")
        workflow.add_edge("dispatch", END)
        
        # Compile with checkpointer for persistence
        checkpointer = DatabaseConfig.get_checkpointer()
        
        return workflow.compile(checkpointer=checkpointer)
    
    def get_compiled_graph(self):
        """Return the compiled graph for execution."""
        if self.graph is None:
            self.graph = self._build_graph()
        return self.graph