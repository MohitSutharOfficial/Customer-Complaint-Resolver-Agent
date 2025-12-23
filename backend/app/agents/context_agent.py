"""
Context Agent - Retrieves and enriches customer context
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from app.agents.base_agent import BaseAgent


class ContextAgent(BaseAgent):
    """Agent responsible for retrieving customer history and context."""
    
    def __init__(self):
        super().__init__(name="ContextAgent", model="gemini-2.0-flash")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve and enrich customer context.
        
        Args:
            input_data: Dict containing:
                - customer_id: Customer identifier
                - customer_data: Optional pre-loaded customer data
                - complaint_history: Optional list of past complaints
        
        Returns:
            Enriched customer context
        """
        customer_id = input_data.get("customer_id")
        customer_data = input_data.get("customer_data", {})
        complaint_history = input_data.get("complaint_history", [])
        
        # Calculate metrics from complaint history
        total_complaints = len(complaint_history)
        resolved_complaints = sum(1 for c in complaint_history if c.get("status") == "resolved")
        
        # Calculate average satisfaction
        satisfaction_scores = [c.get("satisfaction_score") for c in complaint_history if c.get("satisfaction_score")]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
        
        # Analyze sentiment trend
        sentiments = [c.get("sentiment") for c in complaint_history[-5:] if c.get("sentiment")]
        sentiment_trend = self._analyze_sentiment_trend(sentiments)
        
        # Check for recent complaints (same issue)
        recent_complaints = [
            c for c in complaint_history 
            if self._is_recent(c.get("received_at"))
        ]
        
        # Calculate churn risk
        churn_risk = self._calculate_churn_risk(
            total_complaints=total_complaints,
            recent_complaints=len(recent_complaints),
            avg_satisfaction=avg_satisfaction,
            sentiment_trend=sentiment_trend
        )
        
        # Find open/pending complaints
        open_complaints = [
            c for c in complaint_history 
            if c.get("status") in ["new", "in_progress", "pending_review"]
        ]
        
        # Compile context
        context = {
            "customer_id": customer_id,
            "customer_profile": {
                "name": customer_data.get("name"),
                "email": customer_data.get("email"),
                "tier": customer_data.get("tier", "Standard"),
                "lifetime_value": customer_data.get("lifetime_value", 0),
                "preferred_channel": customer_data.get("preferred_channel", "email"),
                "language": customer_data.get("language", "en"),
                "timezone": customer_data.get("timezone", "UTC"),
                "member_since": customer_data.get("created_at")
            },
            "complaint_metrics": {
                "total_complaints": total_complaints,
                "resolved_complaints": resolved_complaints,
                "resolution_rate": resolved_complaints / total_complaints if total_complaints > 0 else 1.0,
                "avg_satisfaction_score": avg_satisfaction,
                "open_complaints_count": len(open_complaints)
            },
            "risk_assessment": {
                "churn_risk_score": churn_risk,
                "sentiment_trend": sentiment_trend,
                "is_repeat_complainant": total_complaints > 2,
                "has_escalation_history": any(c.get("escalated") for c in complaint_history)
            },
            "recent_interactions": [
                {
                    "complaint_id": c.get("external_id"),
                    "date": c.get("received_at"),
                    "category": c.get("categories", ["Unknown"])[0] if c.get("categories") else "Unknown",
                    "status": c.get("status"),
                    "sentiment": c.get("sentiment")
                }
                for c in complaint_history[-3:]
            ],
            "open_complaints": [
                {
                    "complaint_id": c.get("external_id"),
                    "summary": c.get("raw_text", "")[:100],
                    "status": c.get("status"),
                    "received_at": c.get("received_at")
                }
                for c in open_complaints
            ],
            "confidence": 0.9
        }
        
        return context
    
    def _is_recent(self, date_str: Optional[str], days: int = 30) -> bool:
        """Check if a date is within the recent period."""
        if not date_str:
            return False
        try:
            if isinstance(date_str, str):
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                date = date_str
            return date > datetime.now(date.tzinfo) - timedelta(days=days)
        except:
            return False
    
    def _analyze_sentiment_trend(self, sentiments: List[str]) -> str:
        """Analyze sentiment trend from recent complaints."""
        if not sentiments:
            return "unknown"
        
        sentiment_scores = {
            "positive": 4,
            "neutral": 3,
            "frustrated": 2,
            "angry": 1
        }
        
        scores = [sentiment_scores.get(s, 3) for s in sentiments]
        
        if len(scores) < 2:
            return "stable"
        
        # Compare first half to second half
        mid = len(scores) // 2
        first_avg = sum(scores[:mid]) / mid
        second_avg = sum(scores[mid:]) / (len(scores) - mid)
        
        if second_avg < first_avg - 0.5:
            return "declining"
        elif second_avg > first_avg + 0.5:
            return "improving"
        return "stable"
    
    def _calculate_churn_risk(
        self,
        total_complaints: int,
        recent_complaints: int,
        avg_satisfaction: Optional[float],
        sentiment_trend: str
    ) -> float:
        """Calculate customer churn risk score."""
        risk = 0.0
        
        # More complaints = higher risk
        if total_complaints >= 5:
            risk += 0.3
        elif total_complaints >= 3:
            risk += 0.2
        elif total_complaints >= 1:
            risk += 0.1
        
        # Recent complaints increase risk
        if recent_complaints >= 2:
            risk += 0.3
        elif recent_complaints >= 1:
            risk += 0.15
        
        # Low satisfaction increases risk
        if avg_satisfaction:
            if avg_satisfaction < 2:
                risk += 0.3
            elif avg_satisfaction < 3:
                risk += 0.2
            elif avg_satisfaction < 4:
                risk += 0.1
        
        # Declining sentiment increases risk
        if sentiment_trend == "declining":
            risk += 0.2
        
        return min(risk, 1.0)
