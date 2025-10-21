from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import asyncio
import json

from models import Notification, NotificationCreateRequest, NotificationResponse, NotificationType
from repositories.notifications_repository import NotificationsRepository


class NotificationsService:
    def __init__(self, repository: NotificationsRepository):
        self.repository = repository
        self._subscribers: dict = {}  # user_id -> list of SSE connections

    def create_notification(self, notification_data: NotificationCreateRequest) -> NotificationResponse:
        """Create a new notification"""
        notification = Notification(
            userId=notification_data.userId,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            data=notification_data.data
        )
        
        created_notification = self.repository.create_notification(notification)
        
        # Send real-time notification to subscribers
        asyncio.create_task(self._broadcast_to_user(notification_data.userId, created_notification))
        
        return self._to_response(created_notification)

    def get_user_notifications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[NotificationResponse]:
        """Get notifications for a user"""
        return self.repository.get_notifications_by_user(user_id, limit, offset)

    def get_unread_notifications(self, user_id: str) -> List[NotificationResponse]:
        """Get unread notifications for a user"""
        return self.repository.get_unread_notifications_by_user(user_id)

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        return self.repository.mark_notification_as_read(notification_id, user_id)

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        return self.repository.mark_all_notifications_as_read(user_id)

    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        return self.repository.delete_notification(notification_id, user_id)

    def get_notification_count(self, user_id: str) -> dict:
        """Get notification counts for a user"""
        return self.repository.get_notification_count(user_id)

    def subscribe_to_notifications(self, user_id: str, connection):
        """Subscribe a user to real-time notifications"""
        if user_id not in self._subscribers:
            self._subscribers[user_id] = []
        self._subscribers[user_id].append(connection)

    def unsubscribe_from_notifications(self, user_id: str, connection):
        """Unsubscribe a user from real-time notifications"""
        if user_id in self._subscribers:
            try:
                self._subscribers[user_id].remove(connection)
                if not self._subscribers[user_id]:
                    del self._subscribers[user_id]
            except ValueError:
                pass  # Connection not found

    async def _broadcast_to_user(self, user_id: str, notification: Notification):
        """Broadcast notification to all subscribers of a user"""
        if user_id in self._subscribers:
            notification_data = self._to_response(notification)
            message = f"data: {json.dumps(notification_data.dict())}\n\n"
            
            # Send to all connections for this user
            connections_to_remove = []
            for connection in self._subscribers[user_id]:
                try:
                    await connection.put(message)
                except Exception:
                    # Connection is closed, mark for removal
                    connections_to_remove.append(connection)
            
            # Remove closed connections
            for connection in connections_to_remove:
                self.unsubscribe_from_notifications(user_id, connection)

    def _to_response(self, notification: Notification) -> NotificationResponse:
        """Convert Notification to NotificationResponse"""
        return NotificationResponse(
            id=notification.id,
            userId=notification.userId,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            isRead=notification.isRead,
            createdAt=notification.createdAt,
            readAt=notification.readAt
        )

    # Helper methods for creating specific notification types
    def create_booking_notification(self, user_id: str, booking_id: str, notification_type: NotificationType, 
                                  service_title: str, scheduled_at: str = None):
        """Create a booking-related notification"""
        if notification_type == NotificationType.BOOKING_CREATED:
            title = "Booking Confirmed"
            message = f"Your booking for '{service_title}' has been confirmed"
        elif notification_type == NotificationType.BOOKING_UPDATED:
            title = "Booking Updated"
            message = f"Your booking for '{service_title}' has been updated"
        elif notification_type == NotificationType.BOOKING_CANCELLED:
            title = "Booking Cancelled"
            message = f"Your booking for '{service_title}' has been cancelled"
        else:
            title = "Booking Notification"
            message = f"Update for your booking '{service_title}'"

        data = {
            "bookingId": booking_id,
            "serviceTitle": service_title,
            "scheduledAt": scheduled_at
        }

        notification_data = NotificationCreateRequest(
            userId=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )

        return self.create_notification(notification_data)

    def create_payment_notification(self, user_id: str, payment_id: str, notification_type: NotificationType,
                                  amount: float, currency: str, service_title: str = None):
        """Create a payment-related notification"""
        if notification_type == NotificationType.PAYMENT_SUCCESS:
            title = "Payment Successful"
            message = f"Payment of {amount} {currency} has been processed successfully"
        elif notification_type == NotificationType.PAYMENT_FAILED:
            title = "Payment Failed"
            message = f"Payment of {amount} {currency} could not be processed"
        elif notification_type == NotificationType.REFUND_PROCESSED:
            title = "Refund Processed"
            message = f"Refund of {amount} {currency} has been processed"
        else:
            title = "Payment Notification"
            message = f"Payment update: {amount} {currency}"

        data = {
            "paymentId": payment_id,
            "amount": amount,
            "currency": currency,
            "serviceTitle": service_title
        }

        notification_data = NotificationCreateRequest(
            userId=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )

        return self.create_notification(notification_data)

    def create_service_notification(self, user_id: str, service_id: str, notification_type: NotificationType,
                                  service_title: str):
        """Create a service-related notification"""
        if notification_type == NotificationType.SERVICE_CREATED:
            title = "Service Created"
            message = f"Your service '{service_title}' has been created successfully"
        elif notification_type == NotificationType.SERVICE_UPDATED:
            title = "Service Updated"
            message = f"Your service '{service_title}' has been updated"
        elif notification_type == NotificationType.SERVICE_DELETED:
            title = "Service Deleted"
            message = f"Your service '{service_title}' has been deleted"
        else:
            title = "Service Notification"
            message = f"Update for your service '{service_title}'"

        data = {
            "serviceId": service_id,
            "serviceTitle": service_title
        }

        notification_data = NotificationCreateRequest(
            userId=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )

        return self.create_notification(notification_data)
