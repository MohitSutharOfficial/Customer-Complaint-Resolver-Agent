"""
Classifier Agent - Multi-label categorization and sentiment analysis
"""
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent, RateLimitError
import json
import re


class ClassifierAgent(BaseAgent):
    """Agent responsible for classifying complaints into categories and analyzing sentiment."""
    
    CATEGORIES = [
        "Billing",
        "Shipping",
        "Product",
        "Service",
        "Technical",
        "Feedback",
        "Legal",
        "Other"
    ]
    
    SENTIMENTS = ["positive", "neutral", "frustrated", "angry"]
    
    INTENTS = [
        "Refund",
        "Exchange",
        "Information",
        "Complaint",
        "Praise",
        "Escalation",
        "Cancellation",
        "Technical Support"
    ]
    
    # Keywords for rule-based classification
    CATEGORY_KEYWORDS = {
        "Billing": ["bill", "charge", "payment", "invoice", "price", "fee", "refund", "money", "cost"],
        "Shipping": ["ship", "deliver", "arrive", "track", "package", "order", "delay", "late"],
        "Product": ["product", "item", "broken", "defect", "quality", "damage", "wrong"],
        "Service": ["service", "staff", "rude", "help", "support", "agent"],
        "Technical": ["error", "bug", "crash", "login", "password", "app", "website", "not working"],
    }
    
    SENTIMENT_KEYWORDS = {
        "angry": ["angry", "furious", "outraged", "terrible", "worst", "disgusted", "unacceptable"],
        "frustrated": ["frustrated", "annoyed", "disappointed", "upset", "unhappy", "problem", "issue"],
        "positive": ["thank", "great", "excellent", "happy", "love", "amazing", "good"],
    }
    
    def __init__(self):
        super().__init__(name="ClassifierAgent", model="gemini-2.0-flash")
        
        self.system_prompt = f"""You are an expert complaint classifier for a customer service system.
Analyze the complaint and provide classification in JSON format.

Available categories (can select multiple): {', '.join(self.CATEGORIES)}
Available sentiments (select one): {', '.join(self.SENTIMENTS)}
Available intents (select primary): {', '.join(self.INTENTS)}

Return a JSON object with:
{{
    "categories": [list of applicable categories with confidence],
    "primary_category": "the main category",
    "sentiment": "detected sentiment",
    "sentiment_score": 0.0 to 1.0 intensity,
    "intent": "primary intent",
    "secondary_intents": [list of other detected intents],
    "key_issues": [list of specific issues mentioned],
    "emotional_indicators": [list of emotional words/phrases found],
    "escalation_signals": [any threats or escalation mentions],
    "confidence": overall confidence 0.0 to 1.0
}}

Return ONLY valid JSON."""

    def _fallback_classification(self, text: str) -> Dict[str, Any]:
        """Rule-based fallback classification."""
        text_lower = text.lower()
        
        # Detect categories
        categories = []
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                categories.append({"name": category, "confidence": 0.7})
        
        if not categories:
            categories = [{"name": "Other", "confidence": 0.5}]
        
        primary_category = categories[0]["name"]
        
        # Detect sentiment
        sentiment = "neutral"
        sentiment_score = 0.5
        for sent, keywords in self.SENTIMENT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                sentiment = sent
                sentiment_score = 0.7 if sent == "positive" else 0.3
                break
        
        # Detect intent
        intent = "Complaint"
        if "refund" in text_lower:
            intent = "Refund"
        elif "cancel" in text_lower:
            intent = "Cancellation"
        elif "exchange" in text_lower or "replace" in text_lower:
            intent = "Exchange"
        elif any(w in text_lower for w in ["help", "how", "what", "where"]):
            intent = "Information"
        
        return {
            "categories": categories,
            "primary_category": primary_category,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "intent": intent,
            "secondary_intents": [],
            "key_issues": [],
            "emotional_indicators": [],
            "escalation_signals": [],
            "confidence": 0.6
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the complaint. Uses AI when available, falls back to rules."""
        normalized_text = input_data.get("normalized_text", input_data.get("raw_text", ""))
        customer_context = input_data.get("customer_context", {})
        
        try:
            # Build context string
            context_str = ""
            if customer_context:
                context_str = f"\n\nCustomer Context:\n- Previous complaints: {customer_context.get('total_complaints', 0)}\n- Customer tier: {customer_context.get('tier', 'Standard')}"
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Complaint text:\n{normalized_text}{context_str}")
            ]
            
            response = await self.invoke_with_retry(messages)
            classification = json.loads(response.content)
            ai_used = True
        except (RateLimitError, json.JSONDecodeError, Exception):
            classification = self._fallback_classification(normalized_text)
            ai_used = False
        
        # Ensure required fields
        return {
            "categories": classification.get("categories", [{"name": "Other", "confidence": 0.5}]),
            "primary_category": classification.get("primary_category", "Other"),
            "sentiment": classification.get("sentiment", "neutral"),
            "sentiment_score": classification.get("sentiment_score", 0.5),
            "intent": classification.get("intent", "Complaint"),
            "secondary_intents": classification.get("secondary_intents", []),
            "key_issues": classification.get("key_issues", []),
            "emotional_indicators": classification.get("emotional_indicators", []),
            "escalation_signals": classification.get("escalation_signals", []),
            "confidence": classification.get("confidence", 0.5),
            "ai_processed": ai_used
        }
