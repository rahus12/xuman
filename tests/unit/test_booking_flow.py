"""
Unit tests for booking flow including payment processing
Tests the complete booking creation flow with payment
"""
import pytest
from datetime import datetime, timedelta, timezone
from models import BookingCreateRequest, PaymentRequest, PaymentMethod, BookingStatus
from services.bookings_service import BookingsService
from services.payments_service import PaymentsService
from repositories.bookings_repository import BookingsRepository
from repositories.services_repository import ServicesRepository
from repositories.users_repository import UsersRepository
from repositories.payments_repository import PaymentsRepository


class TestBookingFlow:
    """Test complete booking workflow"""
    
    def test_successful_booking_with_payment(self, test_db, sample_consumer, sample_service):
        """Test successful booking creation with payment"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        booking_date = datetime.now(timezone.utc) + timedelta(days=7)
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId="temp",
            amount=sample_service.price,
            currency="USD",
            paymentMethod=payment_method
        )
        
        booking_request = BookingCreateRequest(
            serviceId=sample_service.id,
            scheduledAt=booking_date,
            notes="Test booking",
            payment=payment_request
        )
        
        # Set failure rate to 0 for this test
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
        
        result = booking_service.create_booking("consumer123@example.com", booking_request)
        
        assert result is not None
        assert result.status == BookingStatus.CONFIRMED
        assert result.totalAmount == sample_service.price
        assert result.customerId == sample_consumer.id
        assert result.serviceId == sample_service.id
    
    def test_booking_fails_without_authentication(self, test_db, sample_service):
        """Test booking fails for non-existent user"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        booking_date = datetime.now(timezone.utc) + timedelta(days=7)
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId="temp",
            amount=sample_service.price,
            currency="USD",
            paymentMethod=payment_method
        )
        
        booking_request = BookingCreateRequest(
            serviceId=sample_service.id,
            scheduledAt=booking_date,
            notes="Test booking",
            payment=payment_request
        )
        
        result = booking_service.create_booking("nonexistent@example.com", booking_request)
        
        assert result is None
    
    def test_booking_fails_for_nonexistent_service(self, test_db, sample_consumer):
        """Test booking fails for non-existent service"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        booking_date = datetime.now(timezone.utc) + timedelta(days=7)
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId="temp",
            amount=100.0,
            currency="USD",
            paymentMethod=payment_method
        )
        
        booking_request = BookingCreateRequest(
            serviceId="nonexistent-service-id",
            scheduledAt=booking_date,
            notes="Test booking",
            payment=payment_request
        )
        
        result = booking_service.create_booking("consumer123@example.com", booking_request)
        
        assert result is None
    
    def test_booking_fails_with_payment_failure(self, test_db, sample_consumer, sample_service):
        """Test booking is not created when payment fails"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        booking_date = datetime.now(timezone.utc) + timedelta(days=7)
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId="temp",
            amount=sample_service.price,
            currency="USD",
            paymentMethod=payment_method
        )
        
        booking_request = BookingCreateRequest(
            serviceId=sample_service.id,
            scheduledAt=booking_date,
            notes="Test booking with payment failure",
            payment=payment_request
        )
        
        # Set failure rate to 100% for this test
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "1.0"
        
        result = booking_service.create_booking("consumer123@example.com", booking_request)
        
        # Reset failure rate
        os.environ["PAYMENT_FAILURE_RATE"] = "0.1"
        
        # Booking should fail (return None) when payment fails
        assert result is None
    
    def test_booking_stores_correct_duration(self, test_db, sample_consumer, sample_service):
        """Test booking stores service duration correctly"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        booking_date = datetime.now(timezone.utc) + timedelta(days=7)
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId="temp",
            amount=sample_service.price,
            currency="USD",
            paymentMethod=payment_method
        )
        
        booking_request = BookingCreateRequest(
            serviceId=sample_service.id,
            scheduledAt=booking_date,
            notes="Test booking",
            payment=payment_request
        )
        
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
        
        result = booking_service.create_booking("consumer123@example.com", booking_request)
        
        assert result is not None
        assert result.duration == sample_service.durationMinutes


class TestPaymentProcessing:
    """Test payment processing"""
    
    def test_payment_creates_record(self, test_db, sample_booking):
        """Test payment record is created"""
        payments_repo = PaymentsRepository(test_db)
        payments_service = PaymentsService(payments_repo)
        
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId=sample_booking.id,
            amount=100.0,
            currency="USD",
            paymentMethod=payment_method
        )
        
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
        
        result = payments_service.process_payment(payment_request)
        
        assert result is not None
        assert result.bookingId == sample_booking.id
        assert result.status == "completed"
        assert result.amount == 100.0
    
    def test_payment_can_fail(self, test_db, sample_booking):
        """Test payment can fail randomly"""
        payments_repo = PaymentsRepository(test_db)
        payments_service = PaymentsService(payments_repo)
        
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            cardholderName="Jane Consumer",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123"
        )
        
        payment_request = PaymentRequest(
            bookingId=sample_booking.id,
            amount=100.0,
            currency="USD",
            paymentMethod=payment_method
        )
        
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "1.0"
        
        result = payments_service.process_payment(payment_request)
        
        os.environ["PAYMENT_FAILURE_RATE"] = "0.1"
        
        assert result is not None
        assert result.status == "failed"
        assert result.failureReason is not None

