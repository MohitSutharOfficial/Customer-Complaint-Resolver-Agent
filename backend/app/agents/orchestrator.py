"""
Complaint Resolver Orchestrator - LangGraph workflow for agent coordination
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
import operator
from langgraph.graph import StateGraph, END

from app.agents.intake_agent import IntakeAgent
from app.agents.classifier_agent import ClassifierAgent
from app.agents.priority_agent import PriorityAgent
from app.agents.context_agent import ContextAgent
from app.agents.response_agent import ResponseAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.escalation_agent import EscalationAgent


class ComplaintState(TypedDict):
    """State schema for the complaint resolution workflow."""
    # Input
    raw_text: str
    channel: str
    customer_id: Optional[str]
    customer_data: Optional[Dict[str, Any]]
    complaint_history: Optional[List[Dict[str, Any]]]
    
    # Processed data
    complaint_id: str
    normalized_text: str
    
    # Agent outputs
    intake_result: Dict[str, Any]
    classification: Dict[str, Any]
    priority: Dict[str, Any]
    customer_context: Dict[str, Any]
    response: Dict[str, Any]
    validation: Dict[str, Any]
    escalation: Dict[str, Any]
    
    # Control flow
    iteration_count: int
    max_iterations: int
    validation_passed: bool
    requires_human_review: bool
    
    # Audit trail
    audit_logs: Annotated[List[Dict[str, Any]], operator.add]
    
    # Final output
    final_response: str
    status: str
    error: Optional[str]


class ComplaintOrchestrator:
    """Orchestrates the complaint resolution workflow using LangGraph."""
    
    def __init__(self):
        # Initialize agents
        self.intake_agent = IntakeAgent()
        self.classifier_agent = ClassifierAgent()
        self.priority_agent = PriorityAgent()
        self.context_agent = ContextAgent()
        self.response_agent = ResponseAgent()
        self.validator_agent = ValidatorAgent()
        self.escalation_agent = EscalationAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(ComplaintState)
        
        # Add nodes
        workflow.add_node("intake", self._intake_node)
        workflow.add_node("get_context", self._context_node)
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("prioritize", self._prioritize_node)
        workflow.add_node("generate_response", self._response_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("escalate", self._escalation_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("intake")
        
        # Add edges
        workflow.add_edge("intake", "get_context")
        workflow.add_edge("get_context", "classify")
        workflow.add_edge("classify", "prioritize")
        workflow.add_edge("prioritize", "generate_response")
        workflow.add_edge("generate_response", "validate")
        
        # Conditional edge for validation
        workflow.add_conditional_edges(
            "validate",
            self._should_regenerate,
            {
                "regenerate": "generate_response",
                "continue": "escalate"
            }
        )
        
        workflow.add_edge("escalate", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    async def _intake_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Process incoming complaint through intake agent."""
        result, audit = await self.intake_agent.run_with_audit(
            complaint_id=state.get("complaint_id", "new"),
            action="intake_processing",
            input_data={
                "raw_text": state["raw_text"],
                "channel": state["channel"]
            }
        )
        
        return {
            "complaint_id": result.get("complaint_id", ""),
            "normalized_text": result.get("normalized_text", state["raw_text"]),
            "intake_result": result,
            "audit_logs": [audit]
        }
    
    async def _context_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Retrieve customer context."""
        result, audit = await self.context_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action="context_retrieval",
            input_data={
                "customer_id": state.get("customer_id"),
                "customer_data": state.get("customer_data", {}),
                "complaint_history": state.get("complaint_history", [])
            }
        )
        
        return {
            "customer_context": result,
            "audit_logs": [audit]
        }
    
    async def _classify_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Classify the complaint."""
        result, audit = await self.classifier_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action="classification",
            input_data={
                "normalized_text": state["normalized_text"],
                "customer_context": state.get("customer_context", {})
            }
        )
        
        return {
            "classification": result,
            "audit_logs": [audit]
        }
    
    async def _prioritize_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Calculate priority."""
        result, audit = await self.priority_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action="prioritization",
            input_data={
                "classification": state["classification"],
                "customer_context": state.get("customer_context", {}),
                "urgency_signals": state.get("intake_result", {}).get("urgency_signals", [])
            }
        )
        
        return {
            "priority": result,
            "requires_human_review": result.get("requires_human_review", False),
            "audit_logs": [audit]
        }
    
    async def _response_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Generate response."""
        iteration = state.get("iteration_count", 0) + 1
        previous_feedback = ""
        
        if iteration > 1 and state.get("validation"):
            previous_feedback = state["validation"].get("feedback", "")
        
        result, audit = await self.response_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action=f"response_generation_iter_{iteration}",
            input_data={
                "normalized_text": state["normalized_text"],
                "classification": state["classification"],
                "priority": state["priority"],
                "customer_context": state.get("customer_context", {}),
                "iteration": iteration,
                "previous_feedback": previous_feedback
            }
        )
        
        return {
            "response": result,
            "iteration_count": iteration,
            "audit_logs": [audit]
        }
    
    async def _validate_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Validate the generated response."""
        result, audit = await self.validator_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action=f"validation_iter_{state['iteration_count']}",
            input_data={
                "original_complaint": state["raw_text"],
                "draft_response": state["response"].get("draft_response", ""),
                "classification": state["classification"],
                "priority": state["priority"]
            }
        )
        
        return {
            "validation": result,
            "validation_passed": result.get("approved", False),
            "audit_logs": [audit]
        }
    
    async def _escalation_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Determine escalation path."""
        result, audit = await self.escalation_agent.run_with_audit(
            complaint_id=state["complaint_id"],
            action="escalation_decision",
            input_data={
                "priority": state["priority"],
                "classification": state["classification"],
                "validation": state["validation"],
                "customer_context": state.get("customer_context", {}),
                "iteration_count": state["iteration_count"]
            }
        )
        
        return {
            "escalation": result,
            "requires_human_review": result.get("requires_human_review", False),
            "audit_logs": [audit]
        }
    
    async def _finalize_node(self, state: ComplaintState) -> Dict[str, Any]:
        """Finalize the complaint processing."""
        # Determine final status
        if state.get("escalation", {}).get("should_escalate"):
            status = "escalated"
        elif state.get("validation_passed"):
            if state.get("escalation", {}).get("auto_send_eligible"):
                status = "auto_resolved"
            else:
                status = "pending_review"
        else:
            status = "pending_review"
        
        return {
            "final_response": state.get("response", {}).get("draft_response", ""),
            "status": status
        }
    
    def _should_regenerate(self, state: ComplaintState) -> str:
        """Determine if response should be regenerated."""
        max_iterations = state.get("max_iterations", 3)
        current_iteration = state.get("iteration_count", 0)
        validation_passed = state.get("validation_passed", False)
        
        if validation_passed:
            return "continue"
        
        if current_iteration >= max_iterations:
            return "continue"
        
        return "regenerate"
    
    async def process_complaint(
        self,
        raw_text: str,
        channel: str,
        customer_id: Optional[str] = None,
        customer_data: Optional[Dict[str, Any]] = None,
        complaint_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a complaint through the full workflow.
        
        Args:
            raw_text: The complaint text
            channel: Communication channel (email, chat, social, phone, crm)
            customer_id: Optional customer identifier
            customer_data: Optional pre-loaded customer data
            complaint_history: Optional list of past complaints
        
        Returns:
            Complete processing result including all agent outputs
        """
        initial_state: ComplaintState = {
            "raw_text": raw_text,
            "channel": channel,
            "customer_id": customer_id,
            "customer_data": customer_data or {},
            "complaint_history": complaint_history or [],
            "complaint_id": "",
            "normalized_text": "",
            "intake_result": {},
            "classification": {},
            "priority": {},
            "customer_context": {},
            "response": {},
            "validation": {},
            "escalation": {},
            "iteration_count": 0,
            "max_iterations": 3,
            "validation_passed": False,
            "requires_human_review": False,
            "audit_logs": [],
            "final_response": "",
            "status": "new",
            "error": None
        }
        
        try:
            result = await self.app.ainvoke(initial_state)
            return result
        except Exception as e:
            initial_state["error"] = str(e)
            initial_state["status"] = "error"
            return initial_state


# Create singleton instance
orchestrator = ComplaintOrchestrator()
