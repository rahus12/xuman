from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timezone
import json

from models import Notification, NotificationResponse


class NotificationsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification"""
        query = text("""
            INSERT INTO notifications (id, user_id, type, title, message, data, is_read, created_at, read_at)
            VALUES (:id, :user_id, :type, :title, :message, :data, :is_read, :created_at, :read_at)
        """)
        
        self.db.execute(query, {
            "id": notification.id,
            "user_id": notification.userId,
            "type": notification.type.value,
            "title": notification.title,
            "message": notification.message,
            "data": json.dumps(notification.data) if notification.data else None,
            "is_read": notification.isRead,
            "created_at": notification.createdAt,
            "read_at": notification.readAt
        })
        self.db.commit()
        return notification

    def get_notifications_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[NotificationResponse]:
        """Get notifications for a specific user"""
        query = text("""
            SELECT id, user_id, type, title, message, data, is_read, created_at, read_at
            FROM notifications
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }).fetchall()
        
        return [self._row_to_model(row) for row in result]

    def get_unread_notifications_by_user(self, user_id: str) -> List[NotificationResponse]:
        """Get unread notifications for a specific user"""
        query = text("""
            SELECT id, user_id, type, title, message, data, is_read, created_at, read_at
            FROM notifications
            WHERE user_id = :user_id AND is_read = false
            ORDER BY created_at DESC
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchall()
        return [self._row_to_model(row) for row in result]

    def mark_notification_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        query = text("""
            UPDATE notifications
            SET is_read = true, read_at = :read_at
            WHERE id = :notification_id AND user_id = :user_id
        """)
        
        result = self.db.execute(query, {
            "notification_id": notification_id,
            "user_id": user_id,
            "read_at": datetime.now(timezone.utc)
        })
        self.db.commit()
        return result.rowcount > 0

    def mark_all_notifications_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        query = text("""
            UPDATE notifications
            SET is_read = true, read_at = :read_at
            WHERE user_id = :user_id AND is_read = false
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "read_at": datetime.now(timezone.utc)
        })
        self.db.commit()
        return result.rowcount

    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        query = text("""
            DELETE FROM notifications
            WHERE id = :notification_id AND user_id = :user_id
        """)
        
        result = self.db.execute(query, {
            "notification_id": notification_id,
            "user_id": user_id
        })
        self.db.commit()
        return result.rowcount > 0

    def get_notification_count(self, user_id: str) -> dict:
        """Get notification counts for a user"""
        query = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_read = false THEN 1 END) as unread
            FROM notifications
            WHERE user_id = :user_id
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchone()
        return {
            "total": result.total,
            "unread": result.unread
        }

    def _row_to_model(self, row) -> NotificationResponse:
        """Convert database row to NotificationResponse model"""
        return NotificationResponse(
            id=str(row.id),
            userId=str(row.user_id),
            type=row.type,
            title=row.title,
            message=row.message,
            data=json.loads(row.data) if row.data else None,
            isRead=row.is_read,
            createdAt=row.created_at,
            readAt=row.read_at
        )
