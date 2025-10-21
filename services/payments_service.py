import random
import os
from typing import Optional
from datetime import datetime, timezone

from models import PaymentRequest, PaymentResponse, RefundRequest, RefundResponse, PaymentMethod, NotificationType
from repositories.payments_repository import PaymentsRepository
from services.notifications_service import NotificationsService
from repositories.notifications_repository import NotificationsRepository


class PaymentsService:
    def __init__(self, payments_repo: PaymentsRepository):
        self.payments_repo = payments_repo
        self.notifications_service = NotificationsService(NotificationsRepository(payments_repo.db))

    def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment with configurable random failure rate"""
        # Create payment response
        payment = PaymentResponse(
            bookingId=payment_request.bookingId,
            amount=payment_request.amount,
            currency=payment_request.currency,
            paymentMethod=payment_request.paymentMethod,
            status="pending"
        )

        # Get failure rate from environment variable (default 10%)
        failure_rate = float(os.getenv("PAYMENT_FAILURE_RATE", "0.1"))
        
        # Mock payment processing with configurable failure rate
        if random.random() < failure_rate:
            payment.status = "failed"
            payment.failureReason = self._get_random_failure_reason()
        else:
            payment.status = "completed"

        # Save payment to database
        saved_payment = self.payments_repo.create_payment(payment)
        
        # Send real-time notification
        try:
            # Get user ID from booking (we'll need to modify this to get the actual user)
            # For now, we'll use a placeholder - in a real app, you'd get this from the booking
            user_id = "customer@example.com"  # This should be retrieved from the booking
            
            if saved_payment.status == "completed":
                self.notifications_service.create_payment_notification(
                    user_id=user_id,
                    payment_id=saved_payment.id,
                    notification_type=NotificationType.PAYMENT_SUCCESS,
                    amount=saved_payment.amount,
                    currency=saved_payment.currency
                )
            else:
                self.notifications_service.create_payment_notification(
                    user_id=user_id,
                    payment_id=saved_payment.id,
                    notification_type=NotificationType.PAYMENT_FAILED,
                    amount=saved_payment.amount,
                    currency=saved_payment.currency
                )
        except Exception as e:
            print(f"Payment notification failed: {e}")
        
        return saved_payment

    def process_refund(self, payment_id: str, reason: Optional[str] = None) -> Optional[RefundResponse]:
        """Process refund for a payment"""
        # Get the payment
        payment = self.payments_repo.get_payment(payment_id)
        if not payment:
            return None

        # Check if payment is eligible for refund
        if payment.status != "completed":
            return None

        # Create refund
        refund = RefundResponse(
            paymentId=payment_id,
            status="completed",  # Mock refund always succeeds
            amount=payment.amount,
            reason=reason or "Customer requested refund"
        )

        # Save refund to database
        refund = self.payments_repo.create_refund(refund)

        # Update payment status to refunded
        self.payments_repo.update_payment_status(payment_id, "refunded")
        
        # Send real-time notification
        try:
            # Get user ID from booking (we'll need to modify this to get the actual user)
            # For now, we'll use a placeholder - in a real app, you'd get this from the booking
            user_id = "customer@example.com"  # This should be retrieved from the booking
            
            self.notifications_service.create_payment_notification(
                user_id=user_id,
                payment_id=payment_id,
                notification_type=NotificationType.REFUND_PROCESSED,
                amount=refund.amount,
                currency=payment.currency
            )
        except Exception as e:
            print(f"Refund notification failed: {e}")

        return refund

    def get_payment_status(self, payment_id: str) -> Optional[PaymentResponse]:
        """Get payment status by ID"""
        return self.payments_repo.get_payment(payment_id)

    def get_payment_by_booking(self, booking_id: str) -> Optional[PaymentResponse]:
        """Get payment by booking ID"""
        return self.payments_repo.get_payment_by_booking(booking_id)

    def get_refunds(self, payment_id: str) -> list[RefundResponse]:
        """Get all refunds for a payment"""
        return self.payments_repo.get_refunds_by_payment(payment_id)

    def _get_random_failure_reason(self) -> str:
        """Get a random failure reason for testing"""
        failure_reasons = [
            "Insufficient funds",
            "Card declined by bank",
            "Invalid card number",
            "Expired card",
            "CVV verification failed",
            "Transaction timeout",
            "Network error",
            "Card blocked",
            "Daily limit exceeded",
            "Fraud detection triggered"
        ]
        return random.choice(failure_reasons)

    def validate_payment_method(self, payment_method: PaymentMethod) -> tuple[bool, Optional[str]]:
        """Validate payment method (basic validation)"""
        # Check card number format (basic validation)
        if not payment_method.cardNumber.isdigit():
            return False, "Card number must contain only digits"

        # Check expiry date
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if payment_method.expiryYear < current_year:
            return False, "Card has expired"
        
        if payment_method.expiryYear == current_year and payment_method.expiryMonth < current_month:
            return False, "Card has expired"

        # Check CVV format
        if not payment_method.cvv.isdigit():
            return False, "CVV must contain only digits"

        return True, None
