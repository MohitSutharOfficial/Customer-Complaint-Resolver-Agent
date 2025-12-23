"""
Priority Agent - Calculates complaint priority based on multiple factors
"""
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent


class PriorityAgent(BaseAgent):
    """Agent responsible for calculating complaint priority."""
    
    # Priority level definitions
    PRIORITY_LEVELS = {
        5: "critical",
        4: "high",
        3: "medium",
        2: "low",
        1: "minimal"
    }
    
    # Base priority by category
    CATEGORY_BASE_PRIORITY = {
        "Legal": 4,
        "Billing": 3,
        "Shipping": 3,
        "Product": 2,
        "Technical": 2,
        "Service": 2,
        "Feedback": 1,
        "Other": 2
    }
    
    def __init__(self):
        super().__init__(name="PriorityAgent", model="gemini-2.0-flash")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate priority for a complaint.
        
        Args:
            input_data: Dict containing:
                - classification: Classification results from ClassifierAgent
                - customer_context: Customer history and profile
                - urgency_signals: Detected urgency indicators
                - escalation_signals: Detected escalation threats
        
        Returns:
            Priority assessment with score and reasoning
        """
        classification = input_data.get("classification", {})
        customer_context = input_data.get("customer_context", {})
        urgency_signals = input_data.get("urgency_signals", [])
        escalation_signals = classification.get("escalation_signals", [])
        
        # Calculate base priority from category
        primary_category = classification.get("primary_category", "Other")
        base_priority = self.CATEGORY_BASE_PRIORITY.get(primary_category, 2)
        
        # Initialize factors list
        factors = []
        modifiers = 0
        reasoning_parts = [f"Base priority for {primary_category}: {base_priority}"]
        
        # Sentiment modifier
        sentiment = classification.get("sentiment", "neutral")
        sentiment_score = classification.get("sentiment_score", 0.5)
        
        if sentiment == "angry":
            modifiers += 2
            factors.append("angry_sentiment")
            reasoning_parts.append("+2 for angry sentiment")
        elif sentiment == "frustrated":
            modifiers += 1
            factors.append("frustrated_sentiment")
            reasoning_parts.append("+1 for frustrated sentiment")
        
        # Customer tier modifier
        tier = customer_context.get("tier", "Standard")
        if tier in ["Gold", "Platinum"]:
            modifiers += 1
            factors.append("vip_customer")
            reasoning_parts.append(f"+1 for {tier} tier customer")
        
        # Repeat complaint modifier
        total_complaints = customer_context.get("total_complaints", 0)
        if total_complaints >= 3:
            modifiers += 2
            factors.append("repeat_complaint")
            reasoning_parts.append(f"+2 for repeat complainant ({total_complaints} previous)")
        elif total_complaints >= 1:
            modifiers += 1
            factors.append("previous_complaint")
            reasoning_parts.append(f"+1 for previous complaint history")
        
        # Escalation threat modifier
        if escalation_signals:
            for signal in escalation_signals:
                signal_lower = signal.lower()
                if any(word in signal_lower for word in ["legal", "lawyer", "lawsuit"]):
                    modifiers += 3
                    factors.append("legal_threat")
                    reasoning_parts.append("+3 for legal threat")
                    break
                elif any(word in signal_lower for word in ["chargeback", "dispute", "bank"]):
                    modifiers += 3
                    factors.append("chargeback_threat")
                    reasoning_parts.append("+3 for chargeback threat")
                    break
                elif any(word in signal_lower for word in ["social", "twitter", "review", "post"]):
                    modifiers += 2
                    factors.append("social_media_threat")
                    reasoning_parts.append("+2 for social media threat")
                    break
        
        # Urgency signals modifier
        if urgency_signals:
            modifiers += 1
            factors.append("urgency_detected")
            reasoning_parts.append("+1 for urgency signals")
        
        # Churn risk modifier
        churn_risk = customer_context.get("churn_risk_score", 0)
        if churn_risk > 0.7:
            modifiers += 1
            factors.append("high_churn_risk")
            reasoning_parts.append("+1 for high churn risk")
        
        # High lifetime value modifier
        ltv = customer_context.get("lifetime_value", 0)
        if ltv > 5000:
            modifiers += 1
            factors.append("high_ltv_customer")
            reasoning_parts.append(f"+1 for high LTV (${ltv})")
        
        # Calculate final priority (cap at 5)
        final_priority = min(base_priority + modifiers, 5)
        priority_level = self.PRIORITY_LEVELS.get(final_priority, "medium")
        
        reasoning_parts.append(f"Final priority: {final_priority} ({priority_level})")
        
        return {
            "score": final_priority,
            "level": priority_level,
            "factors": factors,
            "base_priority": base_priority,
            "modifiers": modifiers,
            "reasoning": " | ".join(reasoning_parts),
            "requires_human_review": final_priority >= 4,
            "confidence": 0.95  # Rule-based, high confidence
        }
