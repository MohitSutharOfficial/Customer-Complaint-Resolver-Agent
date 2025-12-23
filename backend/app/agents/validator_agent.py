"""
Validator Agent - Quality checks responses before sending
"""
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent, RateLimitError
import json


class ValidatorAgent(BaseAgent):
    """Agent responsible for validating generated responses."""
    
    def __init__(self):
        super().__init__(name="ValidatorAgent", model="gemini-2.0-flash")
        
        self.system_prompt = """You are a quality assurance specialist reviewing customer service responses.
Evaluate the response against the original complaint and provide detailed feedback.

Check for:
1. COMPLETENESS: Does the response address ALL issues mentioned in the complaint?
2. TONE: Is the tone appropriate for the customer's sentiment?
3. EMPATHY: Does the response show genuine understanding?
4. SPECIFICITY: Are the actions and next steps specific and clear?
5. PROFESSIONALISM: Is the language professional and error-free?
6. PROMISES: Are any promises made realistic and achievable?

Return a JSON object with:
{{
    "approved": true/false,
    "overall_score": 1-10,
    "checks": {{
        "completeness": {{"passed": true/false, "score": 1-10, "notes": "..."}},
        "tone": {{"passed": true/false, "score": 1-10, "notes": "..."}},
        "empathy": {{"passed": true/false, "score": 1-10, "notes": "..."}},
        "specificity": {{"passed": true/false, "score": 1-10, "notes": "..."}},
        "professionalism": {{"passed": true/false, "score": 1-10, "notes": "..."}}
    }},
    "issues": ["list of specific issues found"],
    "suggestions": ["list of specific improvements"],
    "feedback": "overall feedback for regeneration if needed",
    "confidence": 0.0 to 1.0
}}

The response should be approved (approved: true) if:
- Overall score >= 7
- All critical checks passed (completeness, tone)
- No major issues found

Return ONLY valid JSON."""

    def _fallback_validation(self, draft_response: str, classification: Dict) -> Dict:
        """Rule-based validation when AI is unavailable."""
        response_lower = draft_response.lower()
        
        # Basic checks
        has_greeting = any(word in response_lower for word in ["dear", "hello", "hi"])
        has_empathy = any(word in response_lower for word in ["sorry", "apologize", "understand", "frustrat"])
        has_actions = any(word in response_lower for word in ["we are", "we will", "we're", "investigating", "reviewing"])
        has_closing = any(word in response_lower for word in ["regards", "thank", "sincerely", "best"])
        is_long_enough = len(draft_response) > 100
        
        checks = {
            "completeness": {"passed": has_actions, "score": 7 if has_actions else 5, "notes": "Actions included" if has_actions else "Needs more specific actions"},
            "tone": {"passed": True, "score": 7, "notes": "Appears appropriate"},
            "empathy": {"passed": has_empathy, "score": 8 if has_empathy else 5, "notes": "Empathy shown" if has_empathy else "Could show more empathy"},
            "specificity": {"passed": is_long_enough, "score": 7 if is_long_enough else 5, "notes": "Sufficient detail" if is_long_enough else "Could be more detailed"},
            "professionalism": {"passed": has_greeting and has_closing, "score": 8, "notes": "Professional format"}
        }
        
        all_passed = all(check["passed"] for check in checks.values())
        overall_score = sum(check["score"] for check in checks.values()) // 5
        
        return {
            "approved": all_passed and overall_score >= 6,
            "overall_score": overall_score,
            "checks": checks,
            "issues": [] if all_passed else ["Some quality checks need attention"],
            "suggestions": [],
            "feedback": "" if all_passed else "Consider adding more specific details.",
            "confidence": 0.6
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a generated response. Uses AI when available, falls back to rules."""
        original_complaint = input_data.get("original_complaint", "")
        draft_response = input_data.get("draft_response", "")
        classification = input_data.get("classification", {})
        priority = input_data.get("priority", {})
        
        ai_used = False
        try:
            # Build validation context
            context = f"""
Original Complaint:
{original_complaint}

Customer Sentiment: {classification.get('sentiment', 'unknown')}
Categories: {', '.join([c.get('name', c) if isinstance(c, dict) else c for c in classification.get('categories', [])])}
Key Issues: {', '.join(classification.get('key_issues', []))}
Priority: {priority.get('level', 'medium')}

Draft Response:
{draft_response}
"""

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=context)
            ]
            
            response = await self.invoke_with_retry(messages)
            result = json.loads(response.content)
            ai_used = True
        except (RateLimitError, json.JSONDecodeError, Exception):
            # Use fallback validation
            result = self._fallback_validation(draft_response, classification)
        
        # Calculate if needs priority adjustment
        needs_priority_increase = (
            not result.get("approved", True) and 
            result.get("overall_score", 10) < 5
        )
        
        return {
            "approved": result.get("approved", False),
            "overall_score": result.get("overall_score", 5),
            "checks": result.get("checks", {}),
            "issues": result.get("issues", []),
            "suggestions": result.get("suggestions", []),
            "feedback": result.get("feedback", ""),
            "needs_priority_increase": needs_priority_increase,
            "confidence": result.get("confidence", 0.7),
            "ai_processed": ai_used
        }
