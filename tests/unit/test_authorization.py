"""
Unit tests for authorization and access control
Tests role-based access and ownership permissions
"""
import pytest
from models import UserRole, Service, ServiceCreateRequest, ServiceAvailability
from services.services_service import ServicesService
from services.bookings_service import BookingsService
from repositories.services_repository import ServicesRepository
from repositories.bookings_repository import BookingsRepository
from repositories.users_repository import UsersRepository


class TestServiceAuthorization:
    """Test service management authorization"""
    
    def test_provider_can_create_service(self, test_db, sample_provider):
        """Test provider can create their own services"""
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        service_layer = ServicesService(services_repo, users_repo)
        
        service_data = ServiceCreateRequest(
            name="Test Service",
            description="Test Description",
            price=50.0,
            durationMinutes=60,
            availability=ServiceAvailability(
                monday=["09:00", "17:00"]
            )
        )
        
        result = service_layer.create_service("provider123@example.com", service_data)
        
        assert result is not None
        assert result.name == "Test Service"
        assert result.status == "PENDING"
    
    def test_provider_can_update_own_service(self, test_db, sample_provider, sample_service):
        """Test provider can update their own service"""
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        service_layer = ServicesService(services_repo, users_repo)
        
        update_data = ServiceCreateRequest(
            name="Updated Service",
            description="Updated Description",
            price=75.0,
            durationMinutes=90,
            availability=ServiceAvailability(
                monday=["10:00", "18:00"]
            )
        )
        
        result = service_layer.update_service(
            sample_service.id,
            update_data,
            "provider123@example.com"
        )
        
        assert result is not None
        assert result.name == "Updated Service"
        assert result.price == 75.0
    
    def test_provider_cannot_update_others_service(self, test_db, sample_provider, sample_service, other_provider):
        """Test provider cannot update another provider's service"""
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        service_layer = ServicesService(services_repo, users_repo)
        
        update_data = ServiceCreateRequest(
            name="Hacked Service",
            description="Should fail",
            price=1.0,
            durationMinutes=1,
            availability=ServiceAvailability()
        )
        
        result = service_layer.update_service(
            sample_service.id,
            update_data,
            "otherprovider@example.com"
        )
        
        # Should return None (not authorized)
        assert result is None
    
    def test_provider_can_delete_own_service(self, test_db, sample_provider, sample_service):
        """Test provider can delete their own service"""
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        service_layer = ServicesService(services_repo, users_repo)
        
        result = service_layer.delete_service(sample_service.id, "provider123@example.com")
        
        assert result is True
    
    def test_provider_cannot_delete_others_service(self, test_db, sample_provider, sample_service, other_provider):
        """Test provider cannot delete another provider's service"""
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        service_layer = ServicesService(services_repo, users_repo)
        
        result = service_layer.delete_service(sample_service.id, "otherprovider@example.com")
        
        assert result is False


class TestBookingAuthorization:
    """Test booking authorization"""
    
    def test_consumer_can_view_own_booking(self, test_db, sample_consumer, sample_booking):
        """Test consumer can view their own bookings"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.get_booking(sample_booking.id)
        
        assert result is not None
        assert result.customerId == sample_consumer.id
    
    def test_provider_can_view_their_service_bookings(self, test_db, sample_provider, sample_booking):
        """Test provider can view bookings for their services"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.get_booking(sample_booking.id)
        
        assert result is not None
        assert result.providerId == sample_provider.id
    
    def test_consumer_can_cancel_own_booking(self, test_db, sample_consumer, sample_booking):
        """Test consumer can cancel their own booking"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.delete_booking(sample_booking.id, "consumer123@example.com")
        
        assert result is True
    
    def test_provider_can_cancel_their_service_booking(self, test_db, sample_provider, sample_booking):
        """Test provider can cancel bookings for their services"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.delete_booking(sample_booking.id, "provider123@example.com")
        
        assert result is True
    
    def test_other_consumer_cannot_cancel_booking(self, test_db, sample_booking, other_consumer):
        """Test other consumers cannot cancel someone else's booking"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.delete_booking(sample_booking.id, "otherconsumer@example.com")
        
        assert result is False
    
    def test_other_provider_cannot_cancel_booking(self, test_db, sample_booking, other_provider):
        """Test other providers cannot cancel bookings for other services"""
        bookings_repo = BookingsRepository(test_db)
        services_repo = ServicesRepository(test_db)
        users_repo = UsersRepository(test_db)
        booking_service = BookingsService(bookings_repo, services_repo, users_repo)
        
        result = booking_service.delete_booking(sample_booking.id, "otherprovider@example.com")
        
        assert result is False

