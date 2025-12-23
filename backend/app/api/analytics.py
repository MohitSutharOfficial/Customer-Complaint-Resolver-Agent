"""
Analytics API routes
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.core.database import get_db
from app.models.database import Complaint, ComplaintStatus, PriorityLevel, Sentiment
from app.models.schemas import AnalyticsOverview, AgentPerformance

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview for the dashboard."""
    start_date = datetime.utcnow() - timedelta(days=days)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total complaints
    total_result = await db.execute(
        select(func.count(Complaint.id))
        .where(Complaint.received_at >= start_date)
    )
    total_complaints = total_result.scalar() or 0
    
    # Open complaints
    open_result = await db.execute(
        select(func.count(Complaint.id))
        .where(Complaint.status.in_([
            ComplaintStatus.NEW,
            ComplaintStatus.IN_PROGRESS,
            ComplaintStatus.PENDING_REVIEW,
            ComplaintStatus.ESCALATED
        ]))
    )
    open_complaints = open_result.scalar() or 0
    
    # Resolved today
    resolved_today_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.resolved_at >= today_start,
            Complaint.status == ComplaintStatus.RESOLVED
        )
    )
    resolved_today = resolved_today_result.scalar() or 0
    
    # Average response time (in minutes)
    response_time_result = await db.execute(
        select(func.avg(
            func.extract('epoch', Complaint.first_response_at - Complaint.received_at) / 60
        ))
        .where(
            Complaint.first_response_at.isnot(None),
            Complaint.received_at >= start_date
        )
    )
    avg_response_time = response_time_result.scalar() or 0
    
    # SLA compliance rate
    sla_total_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.sla_deadline.isnot(None),
            Complaint.received_at >= start_date
        )
    )
    sla_total = sla_total_result.scalar() or 0
    
    sla_met_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.sla_breached == False,
            Complaint.sla_deadline.isnot(None),
            Complaint.received_at >= start_date
        )
    )
    sla_met = sla_met_result.scalar() or 0
    sla_compliance_rate = (sla_met / sla_total * 100) if sla_total > 0 else 100
    
    # Average satisfaction score
    satisfaction_result = await db.execute(
        select(func.avg(Complaint.satisfaction_score))
        .where(
            Complaint.satisfaction_score.isnot(None),
            Complaint.received_at >= start_date
        )
    )
    avg_satisfaction = satisfaction_result.scalar() or 0
    
    # Complaints trend (daily counts)
    trend_result = await db.execute(
        select(
            func.date(Complaint.received_at).label('date'),
            func.count(Complaint.id).label('count')
        )
        .where(Complaint.received_at >= start_date)
        .group_by(func.date(Complaint.received_at))
        .order_by(func.date(Complaint.received_at))
    )
    complaints_trend = [
        {"date": str(row.date), "count": row.count}
        for row in trend_result
    ]
    
    # Category distribution
    category_result = await db.execute(
        select(
            func.unnest(Complaint.categories).label('category'),
            func.count(Complaint.id).label('count')
        )
        .where(Complaint.received_at >= start_date)
        .group_by('category')
    )
    category_distribution = {row.category: row.count for row in category_result}
    
    # Sentiment distribution
    sentiment_result = await db.execute(
        select(
            Complaint.sentiment,
            func.count(Complaint.id).label('count')
        )
        .where(
            Complaint.sentiment.isnot(None),
            Complaint.received_at >= start_date
        )
        .group_by(Complaint.sentiment)
    )
    sentiment_distribution = {
        row.sentiment.value if row.sentiment else 'unknown': row.count 
        for row in sentiment_result
    }
    
    # Priority distribution
    priority_result = await db.execute(
        select(
            Complaint.priority_level,
            func.count(Complaint.id).label('count')
        )
        .where(Complaint.received_at >= start_date)
        .group_by(Complaint.priority_level)
    )
    priority_distribution = {
        row.priority_level.value if row.priority_level else 'unknown': row.count 
        for row in priority_result
    }
    
    return AnalyticsOverview(
        total_complaints=total_complaints,
        open_complaints=open_complaints,
        resolved_today=resolved_today,
        avg_response_time_minutes=round(avg_response_time, 1),
        sla_compliance_rate=round(sla_compliance_rate, 1),
        avg_satisfaction_score=round(avg_satisfaction, 2),
        complaints_trend=complaints_trend,
        category_distribution=category_distribution,
        sentiment_distribution=sentiment_distribution,
        priority_distribution=priority_distribution
    )


@router.get("/agent-performance", response_model=AgentPerformance)
async def get_agent_performance(
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get AI agent performance metrics."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total processed
    total_result = await db.execute(
        select(func.count(Complaint.id))
        .where(Complaint.received_at >= start_date)
    )
    total = total_result.scalar() or 1  # Avoid division by zero
    
    # Auto-resolved (status = resolved without human intervention)
    auto_resolved_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.status == ComplaintStatus.RESOLVED,
            Complaint.escalated == False,
            Complaint.validation_passed == True,
            Complaint.received_at >= start_date
        )
    )
    auto_resolved = auto_resolved_result.scalar() or 0
    auto_resolved_rate = (auto_resolved / total * 100)
    
    # Human escalation rate
    escalated_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.escalated == True,
            Complaint.received_at >= start_date
        )
    )
    escalated = escalated_result.scalar() or 0
    human_escalation_rate = (escalated / total * 100)
    
    # Average confidence score
    confidence_result = await db.execute(
        select(func.avg(Complaint.classification_confidence))
        .where(
            Complaint.classification_confidence.isnot(None),
            Complaint.received_at >= start_date
        )
    )
    avg_confidence = confidence_result.scalar() or 0
    
    # Validation failure rate (false positives)
    validation_failed_result = await db.execute(
        select(func.count(Complaint.id))
        .where(
            Complaint.validation_passed == False,
            Complaint.received_at >= start_date
        )
    )
    validation_failed = validation_failed_result.scalar() or 0
    false_positive_rate = (validation_failed / total * 100)
    
    # Average iterations
    iterations_result = await db.execute(
        select(func.avg(Complaint.iteration_count))
        .where(Complaint.received_at >= start_date)
    )
    avg_iterations = iterations_result.scalar() or 1
    
    return AgentPerformance(
        auto_resolved_rate=round(auto_resolved_rate, 1),
        human_escalation_rate=round(human_escalation_rate, 1),
        avg_confidence_score=round(avg_confidence, 2),
        false_positive_rate=round(false_positive_rate, 1),
        avg_iterations=round(avg_iterations, 2)
    )
