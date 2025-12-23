"""
API package initialization
"""
from fastapi import APIRouter
from app.api.complaints import router as complaints_router
from app.api.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(complaints_router)
api_router.include_router(analytics_router)

__all__ = ["api_router"]
