"""
Unit tests for booking management functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from models import Booking, BookingStatus, BookingCreateRequest, BookingUpdateRequest, User, UserRole, Service, ServiceAvailability
from services.bookings_service import BookingsService
from repositories.bookings_repository import BookingsRepository
from repositories.services_repository import ServicesRepository
from repositories.users_repository import UsersRepository


class TestBookingService:
    """Test cases for BookingsService"""
    
    def test_list_bookings_success(self, db_session, sample_booking):
        """Test successful booking listing"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking in database
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        result = service.list_bookings()
        
        assert len(result) == 1
        assert result[0].id == sample_booking.id
        assert result[0].customerId == sample_booking.customerId
    
    def test_list_bookings_with_filters(self, db_session, sample_booking):
        """Test booking listing with customer/provider filters"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking in database
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        # Test filtering by customer ID
        customer_bookings = service.list_bookings(customer_id=sample_booking.customerId)
        assert len(customer_bookings) == 1
        assert customer_bookings[0].customerId == sample_booking.customerId
        
        # Test filtering by provider ID
        provider_bookings = service.list_bookings(provider_id=sample_booking.providerId)
        assert len(provider_bookings) == 1
        assert provider_bookings[0].providerId == sample_booking.providerId
    
    def test_get_booking_success(self, db_session, sample_booking):
        """Test successful booking retrieval"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking in database
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        result = service.get_booking(sample_booking.id)
        
        assert result is not None
        assert result.id == sample_booking.id
        assert result.customerId == sample_booking.customerId
    
    def test_get_booking_not_found(self, db_session):
        """Test booking retrieval for non-existent booking"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = service.get_booking("non-existent-id")
        
        assert result is None
    
    def test_create_booking_success(self, db_session, sample_customer, sample_provider, sample_service):
        """Test successful booking creation with payment"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Mock repository methods
        with patch.object(services_repo, 'get_service', return_value=sample_service):
            with patch.object(users_repo, 'get_by_email', side_effect=[sample_customer, sample_provider]):
                with patch.object(service.email_service, 'send_booking_confirmation'):
                    with patch.object(service.email_service, 'send_booking_notification_to_provider'):
                        # Mock payment service
                        with patch('services.bookings_service.PaymentsService') as mock_payments_service:
                            mock_payment = MagicMock()
                            mock_payment.status = "completed"
                            mock_payments_service.return_value.process_payment.return_value = mock_payment
                            
                            booking_data = BookingCreateRequest(
                                serviceId=sample_service.id,
                                scheduledAt=datetime.now(timezone.utc) + timedelta(days=7),
                                notes="Test booking",
                                payment={
                                    "bookingId": "test-payment-id",
                                    "amount": 100.0,
                                    "currency": "USD",
                                    "paymentMethod": {
                                        "type": "card",
                                        "cardNumber": "4111111111111111",
                                        "expiryMonth": 12,
                                        "expiryYear": 2025,
                                        "cvv": "123",
                                        "cardholderName": "Test User"
                                    }
                                }
                            )
                            
                            result = service.create_booking(sample_customer.email, booking_data)
        
        assert result is not None
        assert result.customerId == sample_customer.email
        assert result.serviceId == sample_service.id
        assert result.status == BookingStatus.CONFIRMED  # Auto-confirmed when payment succeeds
    
    def test_create_booking_service_not_found(self, db_session, sample_customer):
        """Test booking creation with non-existent service"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Mock service not found
        with patch.object(services_repo, 'get_service', return_value=None):
            booking_data = BookingCreateRequest(
                serviceId="non-existent-service",
                scheduledAt=datetime.now(timezone.utc) + timedelta(days=7),
                notes="Test booking",
                payment={
                    "bookingId": "test-payment-id",
                    "amount": 100.0,
                    "currency": "USD",
                    "paymentMethod": {
                        "type": "card",
                        "cardNumber": "4111111111111111",
                        "expiryMonth": 12,
                        "expiryYear": 2025,
                        "cvv": "123",
                        "cardholderName": "Test User"
                    }
                }
            )
            
            result = service.create_booking(sample_customer.email, booking_data)
        
        assert result is None
    
    def test_update_booking_success(self, db_session, sample_booking):
        """Test successful booking update with authorization"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking first
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        # Mock repository methods for update
        with patch.object(users_repo, 'get_by_email', return_value=MagicMock()):
            with patch.object(services_repo, 'get_service', return_value=MagicMock()):
                with patch.object(service.email_service, 'send_booking_update'):
                    update_data = BookingUpdateRequest(
                        status=BookingStatus.CONFIRMED,
                        notes="Updated notes"
                    )
                    
                    # Test with authorized user (customer)
                    result = service.update_booking(sample_booking.id, update_data, sample_booking.customerId)
        
        assert result is not None
        assert result.status == BookingStatus.CONFIRMED
        assert result.notes == "Updated notes"
    
    def test_update_booking_not_found(self, db_session):
        """Test booking update for non-existent booking"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        update_data = BookingUpdateRequest(
            status=BookingStatus.CONFIRMED,
            notes="Updated notes"
        )
        
        result = service.update_booking("non-existent-id", update_data, "test@example.com")
        
        assert result is None
    
    def test_update_booking_unauthorized(self, db_session, sample_booking):
        """Test booking update with unauthorized user"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking first
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        update_data = BookingUpdateRequest(
            status=BookingStatus.CONFIRMED,
            notes="Updated notes"
        )
        
        # Test with unauthorized user (different email)
        result = service.update_booking(sample_booking.id, update_data, "unauthorized@example.com")
        
        assert result is None
    
    def test_delete_booking_success(self, db_session, sample_booking):
        """Test successful booking deletion with authorization"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking first
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        # Test with authorized user (customer)
        result = service.delete_booking(sample_booking.id, sample_booking.customerId)
        
        assert result is True
        
        # Verify booking is deleted
        deleted_booking = service.get_booking(sample_booking.id)
        assert deleted_booking is None
    
    def test_delete_booking_not_found(self, db_session):
        """Test booking deletion for non-existent booking"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = service.delete_booking("non-existent-id", "test@example.com")
        
        assert result is False
    
    def test_delete_booking_unauthorized(self, db_session, sample_booking):
        """Test booking deletion with unauthorized user"""
        bookings_repo = BookingsRepository(db_session)
        services_repo = ServicesRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = BookingsService(bookings_repo, services_repo, users_repo)
        
        # Create booking first
        with patch('uuid.uuid4', return_value=sample_booking.id):
            with patch('datetime.datetime.now', return_value=sample_booking.createdAt):
                bookings_repo.create_booking(sample_booking)
        
        # Test with unauthorized user (different email)
        result = service.delete_booking(sample_booking.id, "unauthorized@example.com")
        
        assert result is False


class TestBookingRepository:
    """Test cases for BookingsRepository"""
    
    def test_create_booking_database_error(self, db_session, sample_booking):
        """Test booking creation with database error"""
        repo = BookingsRepository(db_session)
        
        # Mock database error
        with patch.object(db_session, 'execute', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                repo.create_booking(sample_booking)
    
    def test_update_booking_database_error(self, db_session, sample_booking):
        """Test booking update with database error"""
        repo = BookingsRepository(db_session)
        
        # Mock database error
        with patch.object(db_session, 'execute', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                repo.update_booking("test-id", sample_booking)
