from fastapi import APIRouter, HTTPException, Depends, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models import NotificationResponse, NotificationCreateRequest
from services.notifications_service import NotificationsService
from repositories.notifications_repository import NotificationsRepository
from database import get_db
from auth import get_current_user
from services.sse_manager import sse_manager

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notifications_service(db: Session = Depends(get_db)) -> NotificationsService:
    return NotificationsService(NotificationsRepository(db))


@router.get("/stream")
async def stream_notifications(
    request: Request,
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Stream real-time notifications via Server-Sent Events"""
    # Set the notifications service in the SSE manager
    sse_manager.set_notifications_service(notifications_service)
    
    # Create SSE connection for the current user
    return await sse_manager.add_connection(current_user.email, request)


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Get notifications for the current user"""
    return notifications_service.get_user_notifications(current_user.email, limit, offset)


@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Get unread notifications for the current user"""
    return notifications_service.get_unread_notifications(current_user.email)


@router.get("/count")
async def get_notification_count(
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Get notification counts for the current user"""
    return notifications_service.get_notification_count(current_user.email)


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Mark a specific notification as read"""
    success = notifications_service.mark_as_read(notification_id, current_user.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you don't have permission to modify it"
        )
    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Mark all notifications as read for the current user"""
    count = notifications_service.mark_all_as_read(current_user.email)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Delete a specific notification"""
    success = notifications_service.delete_notification(notification_id, current_user.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you don't have permission to delete it"
        )
    return {"message": "Notification deleted"}


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreateRequest,
    current_user = Depends(get_current_user),
    notifications_service: NotificationsService = Depends(get_notifications_service)
):
    """Create a new notification (for testing purposes)"""
    # In a real app, this might be restricted to admin users
    return notifications_service.create_notification(notification_data)
