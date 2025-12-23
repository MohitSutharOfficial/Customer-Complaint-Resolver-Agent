"""
Intake Agent - Normalizes complaints from all channels
"""
from typing import Any, Dict
from datetime import datetime
import uuid
import re
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent, RateLimitError


class IntakeAgent(BaseAgent):
    """Agent responsible for normalizing complaints from various channels."""
    
    # Common urgency keywords
    URGENCY_KEYWORDS = ["urgent", "asap", "immediately", "emergency", "critical", "help", "desperate", "frustrated"]
    
    def __init__(self):
        super().__init__(name="IntakeAgent", model="gemini-2.0-flash")
        
        self.system_prompt = """You are an intake specialist for a customer complaint system.
Your job is to normalize and structure incoming complaints from various channels.

For each complaint, extract and return a JSON object with:
1. cleaned_text: The complaint text, cleaned of any channel-specific formatting
2. language: Detected language code (e.g., "en", "es", "fr")
3. word_count: Number of words in the complaint
4. has_attachments: Boolean indicating if attachments are mentioned
5. contact_info_provided: Boolean if customer provided contact details
6. urgency_signals: List of urgency indicators found (e.g., "URGENT", "ASAP", "immediately")
7. key_entities: List of key entities mentioned (order numbers, product names, dates)

Return ONLY valid JSON, no additional text."""

    def _fallback_analysis(self, raw_text: str) -> Dict[str, Any]:
        """Rule-based fallback when AI is unavailable."""
        text_lower = raw_text.lower()
        
        # Extract urgency signals
        urgency_signals = [word for word in self.URGENCY_KEYWORDS if word in text_lower]
        
        # Extract order numbers (patterns like #12345, ORDER-123, etc.)
        order_patterns = re.findall(r'#?\d{4,}|order[- ]?\d+', text_lower)
        
        # Check for attachment mentions
        has_attachments = any(word in text_lower for word in ["attach", "screenshot", "image", "photo", "file"])
        
        # Check for contact info
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+', raw_text))
        has_phone = bool(re.search(r'\d{10,}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', raw_text))
        
        return {
            "cleaned_text": raw_text.strip(),
            "language": "en",
            "word_count": len(raw_text.split()),
            "has_attachments": has_attachments,
            "contact_info_provided": has_email or has_phone,
            "urgency_signals": urgency_signals,
            "key_entities": order_patterns
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and normalize incoming complaint.
        Uses AI when available, falls back to rules when rate-limited.
        """
        raw_text = input_data.get("raw_text", "")
        channel = input_data.get("channel", "email")
        metadata = input_data.get("metadata", {})
        
        analysis = None
        ai_used = False
        
        try:
            # Try AI analysis
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Channel: {channel}\n\nComplaint text:\n{raw_text}")
            ]
            
            response = await self.invoke_with_retry(messages)
            
            # Parse LLM response
            import json
            analysis = json.loads(response.content)
            ai_used = True
        except (RateLimitError, Exception) as e:
            # Use fallback analysis
            analysis = self._fallback_analysis(raw_text)
        
        # Generate complaint ID
        complaint_id = f"C-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "complaint_id": complaint_id,
            "normalized_text": analysis.get("cleaned_text", raw_text),
            "raw_text": raw_text,
            "channel": channel,
            "language": analysis.get("language", "en"),
            "word_count": analysis.get("word_count", len(raw_text.split())),
            "has_attachments": analysis.get("has_attachments", False),
            "contact_info_provided": analysis.get("contact_info_provided", False),
            "urgency_signals": analysis.get("urgency_signals", []),
            "key_entities": analysis.get("key_entities", []),
            "metadata": metadata,
            "received_at": datetime.utcnow().isoformat(),
            "confidence": 0.95 if ai_used else 0.7,
            "ai_processed": ai_used
        }
