from typing import List, Optional
from datetime import timedelta

from models import (
    Booking,
    BookingCreateRequest,
    BookingResponse,
    BookingUpdateRequest,
    BookingStatus,
    PaymentRequest,
    PaymentResponse,
    NotificationType,
)
from repositories.bookings_repository import BookingsRepository
from repositories.services_repository import ServicesRepository
from repositories.users_repository import UsersRepository
from services.email_service import EmailService
from services.payments_service import PaymentsService
from repositories.payments_repository import PaymentsRepository
from services.notifications_service import NotificationsService
from repositories.notifications_repository import NotificationsRepository


class BookingsService:
    def __init__(self, bookings_repo: BookingsRepository, services_repo: ServicesRepository, users_repo: UsersRepository) -> None:
        self.bookings_repo = bookings_repo
        self.services_repo = services_repo
        self.users_repo = users_repo
        self.email_service = EmailService()
        self.payments_service = PaymentsService(PaymentsRepository(bookings_repo.db))
        self.notifications_service = NotificationsService(NotificationsRepository(bookings_repo.db))

    def list_bookings(self, customer_id: Optional[str] = None, provider_id: Optional[str] = None) -> List[BookingResponse]:
        return [self._to_response(b) for b in self.bookings_repo.list_bookings(customer_id, provider_id)]

    def get_booking(self, booking_id: str) -> Optional[BookingResponse]:
        b = self.bookings_repo.get_booking(booking_id)
        return self._to_response(b) if b else None

    def create_booking(self, customer_id: str, payload: BookingCreateRequest) -> Optional[BookingResponse]:
        """Create a booking with mandatory payment processing - payment must succeed before booking is created"""
        service = self.services_repo.get_service(payload.serviceId)
        if not service:
            return None
        
        # Get customer and provider details for email notifications
        customer = self.users_repo.get_by_email(customer_id)  # customer_id is email
        
        # provider.id is UUID, need to get provider by ID
        provider_user = self.users_repo.get_by_id(service.providerId)  # providerId is UUID
        
        if not customer or not provider_user:
            return None
        
        # Create booking object with PENDING status and save it first
        # (needed because payment has foreign key to bookings)
        customer_uuid = customer.id
        booking = Booking(
            customerId=customer_uuid,
            serviceId=payload.serviceId,
            providerId=service.providerId,
            status=BookingStatus.PENDING,  # Start as pending until payment succeeds
            scheduledAt=payload.scheduledAt,
            duration=service.durationMinutes,
            totalAmount=service.price,
            notes=payload.notes,
        )
        
        # Save booking FIRST (payment table has FK to bookings)
        created = self.bookings_repo.create_booking(booking)
        
        # Create a new PaymentRequest with the actual booking ID
        from models import PaymentRequest
        payment_req = PaymentRequest(
            bookingId=created.id,
            amount=payload.payment.amount,
            currency=payload.payment.currency,
            paymentMethod=payload.payment.paymentMethod
        )
        
        # Process payment - MANDATORY for all bookings
        payments_service = PaymentsService(PaymentsRepository(self.bookings_repo.db))
        payment = payments_service.process_payment(payment_req)

        # If payment fails, delete the booking and process refund
        if payment.status == "failed":
            # Delete the booking since payment failed
            self.bookings_repo.delete_booking(created.id)
            # Process refund for failed payment
            payments_service.process_refund(payment.id, "Payment failed - automatic refund")
            return None

        # Payment succeeded, update booking status to CONFIRMED
        from models import Booking as BookingModel
        updated_booking = BookingModel(
            id=created.id,
            customerId=created.customerId,
            serviceId=created.serviceId,
            providerId=created.providerId,
            status=BookingStatus.CONFIRMED,
            scheduledAt=created.scheduledAt,
            duration=created.duration,
            totalAmount=created.totalAmount,
            notes=created.notes,
            createdAt=created.createdAt,
            updatedAt=created.updatedAt
        )
        created = self.bookings_repo.update_booking(created.id, updated_booking)
        
        # Send email notifications
        try:
            self.email_service.send_booking_confirmation(customer, provider_user, service, created)
            self.email_service.send_booking_notification_to_provider(customer, provider_user, service, created)
        except Exception as e:
            # Log error but don't fail the booking creation
            print(f"Email notification failed: {e}")
        
        # Send real-time notifications
        try:
            # Notify customer
            self.notifications_service.create_booking_notification(
                user_id=customer_id,
                booking_id=created.id,
                notification_type=NotificationType.BOOKING_CREATED,
                service_title=service.name,
                scheduled_at=created.scheduledAt.isoformat() if created.scheduledAt else None
            )
            
            # Notify provider
            self.notifications_service.create_booking_notification(
                user_id=service.providerId,
                booking_id=created.id,
                notification_type=NotificationType.BOOKING_CREATED,
                service_title=service.name,
                scheduled_at=created.scheduledAt.isoformat() if created.scheduledAt else None
            )
        except Exception as e:
            # Log error but don't fail the booking creation
            print(f"Real-time notification failed: {e}")
        
        return self._to_response(created)

    def update_booking(self, booking_id: str, payload: BookingUpdateRequest, current_user_email: str) -> Optional[BookingResponse]:
        """Update a booking with authorization check - only customer or provider can update"""
        existing = self.bookings_repo.get_booking(booking_id)
        if not existing:
            return None
        
        # Get current user's UUID from email
        current_user = self.users_repo.get_by_email(current_user_email)
        if not current_user:
            return None
        
        # Authorization check: only customer or provider can update (compare UUIDs)
        if existing.customerId != current_user.id and existing.providerId != current_user.id:
            return None  # Service layer returns None for unauthorized access
        
        old_status = existing.status
        updated = Booking(
            id=existing.id,
            customerId=existing.customerId,
            serviceId=existing.serviceId,
            providerId=existing.providerId,
            status=payload.status or existing.status,
            scheduledAt=payload.scheduledAt or existing.scheduledAt,
            duration=existing.duration,
            totalAmount=existing.totalAmount,
            notes=payload.notes if payload.notes is not None else existing.notes,
            createdAt=existing.createdAt,
        )
        saved = self.bookings_repo.update_booking(booking_id, updated)
        
        if saved:
            # Send email notification if status changed
            if payload.status and payload.status != old_status:
                try:
                    # Get user details for email (customerId and providerId are UUIDs)
                    customer = self.users_repo.get_by_id(existing.customerId)
                    provider = self.users_repo.get_by_id(existing.providerId)
                    service = self.services_repo.get_service(existing.serviceId)
                    
                    if customer and provider and service:
                        if payload.status == BookingStatus.CANCELLED:
                            self.email_service.send_booking_cancellation(customer, provider, service, saved)
                        else:
                            self.email_service.send_booking_update(customer, provider, service, saved, old_status)
                except Exception as e:
                    print(f"Email notification failed: {e}")
            
            # Send real-time notifications if status changed
            if payload.status and payload.status != old_status:
                try:
                    service = self.services_repo.get_service(existing.serviceId)
                    if service:
                        # Notify customer
                        self.notifications_service.create_booking_notification(
                            user_id=existing.customerId,
                            booking_id=booking_id,
                            notification_type=NotificationType.BOOKING_UPDATED,
                            service_title=service.name,
                            scheduled_at=saved.scheduledAt.isoformat() if saved.scheduledAt else None
                        )
                        
                        # Notify provider
                        self.notifications_service.create_booking_notification(
                            user_id=existing.providerId,
                            booking_id=booking_id,
                            notification_type=NotificationType.BOOKING_UPDATED,
                            service_title=service.name,
                            scheduled_at=saved.scheduledAt.isoformat() if saved.scheduledAt else None
                        )
                except Exception as e:
                    print(f"Real-time notification failed: {e}")
        
        return self._to_response(saved) if saved else None

    def delete_booking(self, booking_id: str, current_user_email: str) -> bool:
        """Delete a booking with authorization check - only customer or provider can delete"""
        existing = self.bookings_repo.get_booking(booking_id)
        if not existing:
            return False
        
        # Get current user's UUID from email
        current_user = self.users_repo.get_by_email(current_user_email)
        if not current_user:
            return False
        
        # Authorization check: only customer or provider can delete (compare UUIDs)
        if existing.customerId != current_user.id and existing.providerId != current_user.id:
            return False  # Service layer returns False for unauthorized access
        
        return self.bookings_repo.delete_booking(booking_id)


    def _to_response(self, b: Booking) -> BookingResponse:
        return BookingResponse(
            id=b.id,
            customerId=b.customerId,
            serviceId=b.serviceId,
            providerId=b.providerId,
            status=b.status,
            scheduledAt=b.scheduledAt,
            duration=b.duration,
            totalAmount=b.totalAmount,
            notes=b.notes,
            createdAt=b.createdAt,
        )


