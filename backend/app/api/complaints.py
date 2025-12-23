"""
Complaints API routes
"""
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.database import Complaint, Customer, AuditLog, ComplaintStatus, PriorityLevel
from app.models.schemas import (
    ComplaintCreate, 
    ComplaintUpdate, 
    ComplaintResponse, 
    ComplaintSummary,
    ComplaintStatusEnum,
    PriorityLevelEnum
)
from app.agents.orchestrator import orchestrator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("/", response_model=dict)
async def create_complaint(
    complaint: ComplaintCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create and process a new complaint through the AI agent pipeline.
    """
    # Get or create customer
    customer = None
    customer_data = {}
    complaint_history = []
    
    if complaint.customer_id:
        result = await db.execute(
            select(Customer).where(Customer.external_id == complaint.customer_id)
        )
        customer = result.scalar_one_or_none()
    
    if not customer and complaint.customer_email:
        result = await db.execute(
            select(Customer).where(Customer.email == complaint.customer_email)
        )
        customer = result.scalar_one_or_none()
    
    if customer:
        customer_data = {
            "name": customer.name,
            "email": customer.email,
            "tier": customer.tier,
            "lifetime_value": customer.lifetime_value,
            "total_complaints": customer.total_complaints,
            "preferred_channel": customer.preferred_channel.value if customer.preferred_channel else "email",
            "language": customer.language,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        }
        
        # Get complaint history
        history_result = await db.execute(
            select(Complaint)
            .where(Complaint.customer_id == customer.id)
            .order_by(desc(Complaint.received_at))
            .limit(10)
        )
        history = history_result.scalars().all()
        complaint_history = [
            {
                "external_id": c.external_id,
                "categories": c.categories,
                "sentiment": c.sentiment.value if c.sentiment else None,
                "status": c.status.value if c.status else None,
                "received_at": c.received_at.isoformat() if c.received_at else None,
                "satisfaction_score": c.satisfaction_score,
                "escalated": c.escalated
            }
            for c in history
        ]
    else:
        # Create new customer
        import uuid
        customer = Customer(
            external_id=complaint.customer_id or f"CUST-{uuid.uuid4().hex[:8].upper()}",
            email=complaint.customer_email,
            name=complaint.customer_name,
            tier="Standard"
        )
        db.add(customer)
        await db.flush()
    
    # Process through orchestrator
    try:
        result = await orchestrator.process_complaint(
            raw_text=complaint.raw_text,
            channel=complaint.channel.value,
            customer_id=customer.external_id,
            customer_data=customer_data,
            complaint_history=complaint_history
        )
        logger.info(f"Orchestrator result: {result}")
    except Exception as e:
        logger.error(f"Orchestrator error: {str(e)}")
        result = {
            "error": str(e),
            "status": "error"
        }
    
    # Create complaint record
    classification = result.get("classification", {})
    priority = result.get("priority", {})
    response = result.get("response", {})
    validation = result.get("validation", {})
    escalation = result.get("escalation", {})
    
    # Generate external_id - ensure it's never empty
    external_id = result.get("complaint_id") or f"C-{uuid.uuid4().hex[:8].upper()}"
    
    # Map priority level
    priority_level_map = {
        "critical": PriorityLevel.CRITICAL,
        "high": PriorityLevel.HIGH,
        "medium": PriorityLevel.MEDIUM,
        "low": PriorityLevel.LOW,
        "minimal": PriorityLevel.MINIMAL
    }
    
    # Map sentiment
    from app.models.database import Sentiment
    sentiment_map = {
        "positive": Sentiment.POSITIVE,
        "neutral": Sentiment.NEUTRAL,
        "frustrated": Sentiment.FRUSTRATED,
        "angry": Sentiment.ANGRY
    }
    
    # Map status
    status_map = {
        "auto_resolved": ComplaintStatus.RESOLVED,
        "pending_review": ComplaintStatus.PENDING_REVIEW,
        "escalated": ComplaintStatus.ESCALATED,
        "error": ComplaintStatus.NEW
    }
    
    db_complaint = Complaint(
        external_id=external_id,
        customer_id=customer.id,
        raw_text=complaint.raw_text,
        channel=complaint.channel,
        language=result.get("intake_result", {}).get("language", "en"),
        categories=[c.get("name", c) if isinstance(c, dict) else c for c in classification.get("categories", [])],
        sentiment=sentiment_map.get(classification.get("sentiment")),
        intent=classification.get("intent"),
        priority_level=priority_level_map.get(priority.get("level"), PriorityLevel.MEDIUM),
        priority_score=priority.get("score", 3),
        priority_factors=priority.get("factors", []),
        status=status_map.get(result.get("status"), ComplaintStatus.NEW),
        escalated=escalation.get("should_escalate", False),
        escalation_reason=", ".join(escalation.get("escalation_reasons", [])) if escalation.get("should_escalate") else None,
        ai_response=response.get("draft_response"),
        recommended_actions=response.get("recommended_actions", []),
        classification_confidence=classification.get("confidence"),
        response_confidence=response.get("confidence"),
        validation_passed=validation.get("approved"),
        validation_feedback=validation.get("feedback"),
        iteration_count=result.get("iteration_count", 0),
        sla_deadline=datetime.fromisoformat(escalation.get("sla_deadline")) if escalation.get("sla_deadline") else None,
        assigned_to=escalation.get("assigned_team")
    )
    
    db.add(db_complaint)
    
    # Update customer complaint count
    customer.total_complaints += 1
    
    # Flush to get the complaint ID without full commit
    await db.flush()
    
    # Create audit logs (now complaint_id is available)
    for audit in result.get("audit_logs", []):
        db_audit = AuditLog(
            complaint_id=db_complaint.id,
            agent_name=audit.get("agent_name"),
            action=audit.get("action"),
            input_data=audit.get("input_data"),
            output_data=audit.get("output_data"),
            confidence=audit.get("confidence"),
            model_version=audit.get("model_version"),
            execution_time_ms=audit.get("execution_time_ms"),
            error=audit.get("error")
        )
        db.add(db_audit)
    
    await db.commit()
    await db.refresh(db_complaint)
    
    return {
        "complaint_id": str(db_complaint.id),
        "external_id": db_complaint.external_id,
        "status": db_complaint.status.value,
        "priority": {
            "level": db_complaint.priority_level.value,
            "score": db_complaint.priority_score,
            "factors": db_complaint.priority_factors
        },
        "classification": {
            "categories": db_complaint.categories,
            "sentiment": db_complaint.sentiment.value if db_complaint.sentiment else None,
            "intent": db_complaint.intent,
            "confidence": db_complaint.classification_confidence
        },
        "response": {
            "draft": db_complaint.ai_response,
            "recommended_actions": db_complaint.recommended_actions,
            "confidence": db_complaint.response_confidence,
            "validation_passed": db_complaint.validation_passed
        },
        "escalation": {
            "escalated": db_complaint.escalated,
            "reason": db_complaint.escalation_reason,
            "assigned_to": db_complaint.assigned_to,
            "sla_deadline": db_complaint.sla_deadline.isoformat() if db_complaint.sla_deadline else None
        }
    }


@router.get("/", response_model=List[ComplaintSummary])
async def list_complaints(
    status: Optional[ComplaintStatusEnum] = None,
    priority: Optional[PriorityLevelEnum] = None,
    channel: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List complaints with optional filtering."""
    query = select(Complaint).options(selectinload(Complaint.customer))
    
    if status:
        query = query.where(Complaint.status == status.value)
    if priority:
        query = query.where(Complaint.priority_level == priority.value)
    if channel:
        query = query.where(Complaint.channel == channel)
    
    query = query.order_by(desc(Complaint.priority_score), desc(Complaint.received_at))
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    complaints = result.scalars().all()
    
    return [
        ComplaintSummary(
            id=c.id,
            external_id=c.external_id,
            customer_name=c.customer.name if c.customer else None,
            raw_text=c.raw_text[:200] + "..." if len(c.raw_text) > 200 else c.raw_text,
            channel=c.channel,
            priority_level=c.priority_level,
            priority_score=c.priority_score,
            sentiment=c.sentiment,
            status=c.status,
            categories=c.categories,
            received_at=c.received_at,
            sla_deadline=c.sla_deadline,
            sla_breached=c.sla_breached
        )
        for c in complaints
    ]


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific complaint by ID."""
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: UUID,
    update: ComplaintUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a complaint."""
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Update fields
    if update.status:
        complaint.status = update.status
        if update.status == ComplaintStatusEnum.RESOLVED:
            complaint.resolved_at = datetime.utcnow()
    if update.assigned_to:
        complaint.assigned_to = update.assigned_to
    if update.final_response:
        complaint.final_response = update.final_response
        if not complaint.first_response_at:
            complaint.first_response_at = datetime.utcnow()
    if update.resolution_summary:
        complaint.resolution_summary = update.resolution_summary
    if update.satisfaction_score is not None:
        complaint.satisfaction_score = update.satisfaction_score
    
    await db.commit()
    await db.refresh(complaint)
    
    return complaint


@router.get("/{complaint_id}/audit", response_model=List[dict])
async def get_complaint_audit_log(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for a complaint."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.complaint_id == complaint_id)
        .order_by(AuditLog.created_at)
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": str(log.id),
            "agent_name": log.agent_name,
            "action": log.action,
            "confidence": log.confidence,
            "execution_time_ms": log.execution_time_ms,
            "error": log.error,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
