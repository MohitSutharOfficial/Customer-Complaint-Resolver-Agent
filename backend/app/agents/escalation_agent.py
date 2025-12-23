"""
Escalation Agent - Determines if and how to escalate complaints
"""
from typing import Any, Dict, List
from datetime import datetime, timedelta
from app.agents.base_agent import BaseAgent


class EscalationAgent(BaseAgent):
    """Agent responsible for making escalation decisions."""
    
    # Escalation team assignments
    TEAM_ASSIGNMENTS = {
        "Billing": "billing_team",
        "Shipping": "logistics_team",
        "Product": "product_team",
        "Technical": "technical_support",
        "Legal": "legal_team",
        "Service": "customer_success",
        "Feedback": "product_feedback",
        "Other": "general_support"
    }
    
    # SLA definitions by priority (in minutes)
    SLA_TARGETS = {
        "critical": 60,    # 1 hour
        "high": 240,       # 4 hours
        "medium": 480,     # 8 hours
        "low": 1440,       # 24 hours
        "minimal": 2880    # 48 hours
    }
    
    def __init__(self):
        super().__init__(name="EscalationAgent", model="gemini-2.0-flash")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine escalation path and routing.
        
        Args:
            input_data: Dict containing:
                - priority: Priority assessment
                - classification: Classification results
                - validation: Validation results
                - customer_context: Customer context
                - iteration_count: Number of response iterations
        
        Returns:
            Escalation decision with routing information
        """
        priority = input_data.get("priority", {})
        classification = input_data.get("classification", {})
        validation = input_data.get("validation", {})
        customer_context = input_data.get("customer_context", {})
        iteration_count = input_data.get("iteration_count", 0)
        
        priority_level = priority.get("level", "medium")
        priority_score = priority.get("score", 3)
        primary_category = classification.get("primary_category", "Other")
        
        # Determine base team assignment
        assigned_team = self.TEAM_ASSIGNMENTS.get(primary_category, "general_support")
        
        # Initialize escalation decision
        should_escalate = False
        escalation_level = 0  # 0 = no escalation, 1 = team lead, 2 = supervisor, 3 = manager
        escalation_reasons = []
        
        # Check priority-based escalation
        if priority_score >= 5:
            should_escalate = True
            escalation_level = max(escalation_level, 2)
            escalation_reasons.append("Critical priority complaint")
        elif priority_score >= 4:
            should_escalate = True
            escalation_level = max(escalation_level, 1)
            escalation_reasons.append("High priority complaint")
        
        # Check validation failure escalation
        if not validation.get("approved", True) and iteration_count >= 3:
            should_escalate = True
            escalation_level = max(escalation_level, 1)
            escalation_reasons.append("Response generation failed after max iterations")
        
        # Check legal/compliance escalation
        if primary_category == "Legal" or "legal_threat" in priority.get("factors", []):
            should_escalate = True
            escalation_level = max(escalation_level, 3)
            escalation_reasons.append("Legal/compliance concern")
            assigned_team = "legal_team"
        
        # Check VIP customer escalation
        customer_profile = customer_context.get("customer_profile", {})
        if customer_profile.get("tier") in ["Gold", "Platinum"]:
            escalation_level = max(escalation_level, 1)
            if priority_score >= 4:
                escalation_reasons.append("VIP customer")
        
        # Check repeat complainant escalation
        risk_assessment = customer_context.get("risk_assessment", {})
        if risk_assessment.get("is_repeat_complainant") and risk_assessment.get("sentiment_trend") == "declining":
            should_escalate = True
            escalation_level = max(escalation_level, 1)
            escalation_reasons.append("Repeat complainant with declining sentiment")
        
        # Check high churn risk escalation
        if risk_assessment.get("churn_risk_score", 0) > 0.7:
            escalation_level = max(escalation_level, 1)
            escalation_reasons.append("High churn risk")
        
        # Calculate SLA deadline
        sla_minutes = self.SLA_TARGETS.get(priority_level, 480)
        sla_deadline = datetime.utcnow() + timedelta(minutes=sla_minutes)
        
        # Determine assigned agent level
        agent_levels = {
            0: "ai_auto",
            1: "team_lead",
            2: "supervisor",
            3: "manager"
        }
        assigned_level = agent_levels.get(escalation_level, "ai_auto")
        
        # Determine auto-send eligibility
        auto_send = (
            not should_escalate and 
            validation.get("approved", False) and 
            priority_score <= 3
        )
        
        # Build action recommendations
        action_recommendations = []
        if should_escalate:
            action_recommendations.append(f"Route to {assigned_level} for review")
        if priority_score >= 4:
            action_recommendations.append("Monitor for SLA compliance")
        if risk_assessment.get("churn_risk_score", 0) > 0.5:
            action_recommendations.append("Schedule follow-up check")
        if not validation.get("approved", True):
            action_recommendations.append("Require human review of response before sending")
        
        return {
            "should_escalate": should_escalate,
            "escalation_level": escalation_level,
            "escalation_level_name": assigned_level,
            "escalation_reasons": escalation_reasons,
            "assigned_team": assigned_team,
            "sla_deadline": sla_deadline.isoformat(),
            "sla_minutes": sla_minutes,
            "auto_send_eligible": auto_send,
            "requires_human_review": should_escalate or priority_score >= 4,
            "action_recommendations": action_recommendations,
            "routing_decision": {
                "type": "escalate" if should_escalate else ("auto_send" if auto_send else "queue_for_review"),
                "destination": assigned_team,
                "priority_flag": priority_level in ["critical", "high"]
            },
            "confidence": 0.95
        }
