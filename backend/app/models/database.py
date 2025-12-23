"""
Database models for Customer Complaint Resolver Agent
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

Base = declarative_base()


class ComplaintStatus(str, enum.Enum):
    """Complaint status enum."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PriorityLevel(str, enum.Enum):
    """Priority level enum."""
    CRITICAL = "critical"  # 5
    HIGH = "high"  # 4
    MEDIUM = "medium"  # 3
    LOW = "low"  # 2
    MINIMAL = "minimal"  # 1


class Channel(str, enum.Enum):
    """Communication channel enum."""
    EMAIL = "email"
    CHAT = "chat"
    SOCIAL = "social"
    PHONE = "phone"
    CRM = "crm"


class Sentiment(str, enum.Enum):
    """Sentiment enum."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class Customer(Base):
    """Customer model."""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    email = Column(String(255), index=True)
    name = Column(String(255))
    tier = Column(String(50), default="Standard")  # Standard, Silver, Gold, Platinum
    lifetime_value = Column(Float, default=0.0)
    total_complaints = Column(Integer, default=0)
    resolved_complaints = Column(Integer, default=0)
    avg_satisfaction_score = Column(Float, nullable=True)
    preferred_channel = Column(SQLEnum(Channel), default=Channel.EMAIL)
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    churn_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    complaints = relationship("Complaint", back_populates="customer")


class Complaint(Base):
    """Complaint model."""
    __tablename__ = "complaints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    
    # Content
    raw_text = Column(Text, nullable=False)
    channel = Column(SQLEnum(Channel), nullable=False)
    language = Column(String(10), default="en")
    
    # Classification
    categories = Column(JSON, default=list)  # List of categories
    sentiment = Column(SQLEnum(Sentiment), nullable=True)
    intent = Column(String(100), nullable=True)
    
    # Priority
    priority_level = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM)
    priority_score = Column(Integer, default=3)
    priority_factors = Column(JSON, default=list)
    
    # Status tracking
    status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.NEW)
    assigned_to = Column(String(100), nullable=True)
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    
    # Response
    ai_response = Column(Text, nullable=True)
    final_response = Column(Text, nullable=True)
    recommended_actions = Column(JSON, default=list)
    
    # Confidence and validation
    classification_confidence = Column(Float, nullable=True)
    response_confidence = Column(Float, nullable=True)
    validation_passed = Column(Boolean, nullable=True)
    validation_feedback = Column(Text, nullable=True)
    
    # Iteration tracking
    iteration_count = Column(Integer, default=0)
    
    # SLA tracking
    sla_deadline = Column(DateTime, nullable=True)
    sla_breached = Column(Boolean, default=False)
    
    # Resolution
    resolution_summary = Column(Text, nullable=True)
    satisfaction_score = Column(Float, nullable=True)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="complaints")
    audit_logs = relationship("AuditLog", back_populates="complaint")


class AuditLog(Base):
    """Audit log for tracking all agent decisions."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)
    
    agent_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    model_version = Column(String(100), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = relationship("Complaint", back_populates="audit_logs")


class ResponseTemplate(Base):
    """Pre-defined response templates."""
    __tablename__ = "response_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    sentiment_target = Column(SQLEnum(Sentiment), nullable=True)
    template_text = Column(Text, nullable=False)
    variables = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentSession(Base):
    """Short-term memory for agent sessions."""
    __tablename__ = "agent_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)
    
    current_state = Column(String(100), nullable=False)
    iteration_count = Column(Integer, default=0)
    max_iterations = Column(Integer, default=3)
    
    # Agent outputs stored as JSON
    agent_outputs = Column(JSON, default=dict)
    
    # Flags
    requires_human_review = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    sla_at_risk = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
