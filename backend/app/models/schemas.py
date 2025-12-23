"""
Pydantic schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum


# Enums
class ComplaintStatusEnum(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PriorityLevelEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ChannelEnum(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    SOCIAL = "social"
    PHONE = "phone"
    CRM = "crm"


class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


# Customer Schemas
class CustomerBase(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    tier: str = "Standard"
    preferred_channel: ChannelEnum = ChannelEnum.EMAIL
    language: str = "en"


class CustomerCreate(CustomerBase):
    external_id: str


class CustomerResponse(CustomerBase):
    id: UUID
    external_id: str
    lifetime_value: float
    total_complaints: int
    resolved_complaints: int
    avg_satisfaction_score: Optional[float]
    churn_risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# Complaint Schemas
class ComplaintCreate(BaseModel):
    """Schema for creating a new complaint."""
    raw_text: str = Field(..., min_length=1, description="The complaint text")
    channel: ChannelEnum = Field(..., description="Communication channel")
    customer_id: Optional[str] = Field(None, description="External customer ID")
    customer_email: Optional[str] = Field(None, description="Customer email if ID not provided")
    customer_name: Optional[str] = Field(None, description="Customer name")


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint."""
    status: Optional[ComplaintStatusEnum] = None
    assigned_to: Optional[str] = None
    final_response: Optional[str] = None
    resolution_summary: Optional[str] = None
    satisfaction_score: Optional[float] = None


class ClassificationResult(BaseModel):
    """Classification output from classifier agent."""
    categories: List[str]
    sentiment: SentimentEnum
    intent: str
    confidence: float


class PriorityResult(BaseModel):
    """Priority output from priority agent."""
    score: int = Field(..., ge=1, le=5)
    level: PriorityLevelEnum
    factors: List[str]
    reasoning: str


class ResponseResult(BaseModel):
    """Response output from response agent."""
    draft_response: str
    recommended_actions: List[str]
    confidence: float
    tone: str


class ValidationResult(BaseModel):
    """Validation output from validator agent."""
    approved: bool
    feedback: str
    issues: List[str]
    suggestions: List[str]


class AgentOutput(BaseModel):
    """Combined agent outputs."""
    classification: Optional[ClassificationResult] = None
    priority: Optional[PriorityResult] = None
    response: Optional[ResponseResult] = None
    validation: Optional[ValidationResult] = None


class ComplaintResponse(BaseModel):
    """Full complaint response."""
    id: UUID
    external_id: str
    customer_id: UUID
    raw_text: str
    channel: ChannelEnum
    language: str
    
    # Classification
    categories: List[str]
    sentiment: Optional[SentimentEnum]
    intent: Optional[str]
    
    # Priority
    priority_level: PriorityLevelEnum
    priority_score: int
    priority_factors: List[str]
    
    # Status
    status: ComplaintStatusEnum
    assigned_to: Optional[str]
    escalated: bool
    escalation_reason: Optional[str]
    
    # Response
    ai_response: Optional[str]
    final_response: Optional[str]
    recommended_actions: List[str]
    
    # Confidence
    classification_confidence: Optional[float]
    response_confidence: Optional[float]
    validation_passed: Optional[bool]
    
    # SLA
    sla_deadline: Optional[datetime]
    sla_breached: bool
    
    # Timestamps
    received_at: datetime
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ComplaintSummary(BaseModel):
    """Summary view for complaint list."""
    id: UUID
    external_id: str
    customer_name: Optional[str]
    raw_text: str
    channel: ChannelEnum
    priority_level: PriorityLevelEnum
    priority_score: int
    sentiment: Optional[SentimentEnum]
    status: ComplaintStatusEnum
    categories: List[str]
    received_at: datetime
    sla_deadline: Optional[datetime]
    sla_breached: bool

    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsOverview(BaseModel):
    """Dashboard analytics overview."""
    total_complaints: int
    open_complaints: int
    resolved_today: int
    avg_response_time_minutes: float
    sla_compliance_rate: float
    avg_satisfaction_score: float
    
    # Trends
    complaints_trend: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]


class AgentPerformance(BaseModel):
    """AI agent performance metrics."""
    auto_resolved_rate: float
    human_escalation_rate: float
    avg_confidence_score: float
    false_positive_rate: float
    avg_iterations: float


# Session State Schema
class SessionState(BaseModel):
    """Agent session state."""
    session_id: UUID
    complaint_id: UUID
    current_state: str
    iteration_count: int
    max_iterations: int
    agent_outputs: AgentOutput
    flags: Dict[str, bool]
    created_at: datetime
    updated_at: datetime
