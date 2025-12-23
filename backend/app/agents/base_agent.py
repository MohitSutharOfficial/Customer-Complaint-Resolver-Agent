"""
Base Agent class for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
import time
import uuid
import asyncio
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when AI API rate limit is hit and retries exhausted."""
    pass


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    # Rate limit retry settings - FAST FAIL for better UX
    MAX_RETRIES = 2
    BASE_DELAY = 1.0  # seconds
    MAX_DELAY = 5.0  # seconds
    
    def __init__(self, name: str, model: str = "gemini-2.0-flash"):
        self.name = name
        self.model = model
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0.3,
            google_api_key=settings.google_api_key
        )
    
    async def invoke_with_retry(self, messages: List[BaseMessage]) -> Any:
        """
        Invoke LLM with quick retry for rate limits.
        Fails fast to allow fallback processing.
        
        Args:
            messages: List of messages to send to the LLM
            
        Returns:
            LLM response
            
        Raises:
            RateLimitError: When rate limited and retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.llm.ainvoke(messages)
                return response
            except Exception as e:
                error_str = str(e)
                last_exception = e
                
                # Check if it's a rate limit error
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    if attempt < self.MAX_RETRIES - 1:
                        delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
                        logger.warning(
                            f"{self.name}: Rate limited (attempt {attempt + 1}/{self.MAX_RETRIES}). "
                            f"Waiting {delay:.1f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        # Final attempt failed - raise RateLimitError for fallback
                        logger.warning(f"{self.name}: Rate limit - using fallback processing")
                        raise RateLimitError(f"AI rate limited after {self.MAX_RETRIES} attempts")
                else:
                    # Not a rate limit error, re-raise immediately
                    raise
        
        raise RateLimitError(f"AI unavailable after {self.MAX_RETRIES} attempts")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass
    
    def create_audit_entry(
        self,
        complaint_id: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        confidence: Optional[float] = None,
        execution_time_ms: Optional[int] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an audit log entry."""
        return {
            "id": str(uuid.uuid4()),
            "complaint_id": complaint_id,
            "agent_name": self.name,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "confidence": confidence,
            "model_version": self.model,
            "execution_time_ms": execution_time_ms,
            "error": error,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def run_with_audit(
        self,
        complaint_id: str,
        action: str,
        input_data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run the agent and create an audit entry."""
        start_time = time.time()
        error = None
        output_data = {}
        confidence = None
        
        try:
            output_data = await self.execute(input_data)
            confidence = output_data.get("confidence")
        except Exception as e:
            error = str(e)
            output_data = {"error": error}
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        audit_entry = self.create_audit_entry(
            complaint_id=complaint_id,
            action=action,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            error=error
        )
        
        return output_data, audit_entry
