import pytest
from unittest.mock import patch
from models import Service, ServiceCreateRequest, ServiceResponse, ServiceAvailability
from repositories.services_repository import ServicesRepository
from services.services_service import ServicesService
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone

class TestServiceService:
    """Test cases for ServicesService"""

    def test_create_service_success(self, db_session, sample_provider, sample_service_availability):
        """Test successful service creation"""
        service = ServicesService(ServicesRepository(db_session))

        service_data = ServiceCreateRequest(
            providerId=sample_provider.id,
            title="Test Service",
            description="A test service description",
            category="consulting",
            price=100.0,
            currency="USD",
            duration=60,
            availability=sample_service_availability,
            images=["image1.jpg", "image2.jpg"]
        )

        result = service.create_service(service_data)

        assert result is not None
        assert result.title == "Test Service"
        assert result.providerId == sample_provider.id
        assert result.price == 100.0

    def test_get_service_success(self, db_session, sample_service):
        """Test getting a service by ID"""
        service = ServicesService(ServicesRepository(db_session))

        # Create service in database
        service_data = ServiceCreateRequest(
            providerId=sample_service.providerId,
            title=sample_service.title,
            description=sample_service.description,
            category=sample_service.category,
            price=sample_service.price,
            currency=sample_service.currency,
            duration=sample_service.duration,
            availability=sample_service.availability,
            images=sample_service.images
        )
        created_service = service.create_service(service_data)

        result = service.get_service(created_service.id)

        assert result is not None
        assert result.id == created_service.id
        assert result.title == sample_service.title

    def test_get_service_not_found(self, db_session):
        """Test getting a non-existent service"""
        service = ServicesService(ServicesRepository(db_session))
        result = service.get_service("nonexistent-service-id")
        assert result is None

    def test_list_services(self, db_session, sample_provider, sample_service_availability):
        """Test listing all services"""
        service = ServicesService(ServicesRepository(db_session))

        # Create multiple services
        service_data1 = ServiceCreateRequest(
            providerId=sample_provider.id,
            title="Service 1",
            description="Description 1",
            category="consulting",
            price=100.0,
            currency="USD",
            duration=60,
            availability=sample_service_availability,
            images=[]
        )

        service_data2 = ServiceCreateRequest(
            providerId=sample_provider.id,
            title="Service 2",
            description="Description 2",
            category="design",
            price=200.0,
            currency="USD",
            duration=120,
            availability=sample_service_availability,
            images=[]
        )

        service.create_service(service_data1)
        service.create_service(service_data2)

        services = service.list_services()
        assert len(services) == 2
        assert any(s.title == "Service 1" for s in services)
        assert any(s.title == "Service 2" for s in services)

    def test_update_service_success(self, db_session, sample_provider, sample_service_availability):
        """Test successful service update"""
        service = ServicesService(ServicesRepository(db_session))

        # Create service
        service_data = ServiceCreateRequest(
            providerId=sample_provider.id,
            title="Original Title",
            description="Original Description",
            category="consulting",
            price=100.0,
            currency="USD",
            duration=60,
            availability=sample_service_availability,
            images=[]
        )
        created_service = service.create_service(service_data)

        # Update service
        from models import ServiceUpdateRequest
        update_data = ServiceUpdateRequest(
            title="Updated Title",
            description="Updated Description",
            price=150.0
        )

        result = service.update_service(created_service.id, update_data)

        assert result is not None
        assert result.title == "Updated Title"
        assert result.description == "Updated Description"
        assert result.price == 150.0

    def test_update_service_not_found(self, db_session, sample_provider, sample_service_availability):
        """Test updating a non-existent service"""
        service = ServicesService(ServicesRepository(db_session))

        from models import ServiceUpdateRequest
        update_data = ServiceUpdateRequest(
            title="Updated Title",
            price=150.0
        )

        result = service.update_service("nonexistent-service-id", update_data)
        assert result is None

    def test_delete_service_success(self, db_session, sample_provider, sample_service_availability):
        """Test successful service deletion"""
        service = ServicesService(ServicesRepository(db_session))

        # Create service
        service_data = ServiceCreateRequest(
            providerId=sample_provider.id,
            title="Service to Delete",
            description="Description",
            category="consulting",
            price=100.0,
            currency="USD",
            duration=60,
            availability=sample_service_availability,
            images=[]
        )
        created_service = service.create_service(service_data)

        # Delete service
        result = service.delete_service(created_service.id)
        assert result is True

        # Verify service is deleted
        deleted_service = service.get_service(created_service.id)
        assert deleted_service is None

    def test_delete_service_not_found(self, db_session):
        """Test deleting a non-existent service"""
        service = ServicesService(ServicesRepository(db_session))
        result = service.delete_service("nonexistent-service-id")
        assert result is False


class TestServiceRepository:
    """Test cases for ServicesRepository"""

    def test_create_service_database_error(self, db_session, sample_service):
        """Test database error during service creation"""
        repo = ServicesRepository(db_session)
        with patch.object(db_session, 'execute', side_effect=IntegrityError("mock", {}, {})):
            with pytest.raises(ValueError, match="Service creation failed"):
                repo.create_service(sample_service)

    def test_update_service_database_error(self, db_session, sample_service):
        """Test database error during service update"""
        repo = ServicesRepository(db_session)
        with patch.object(db_session, 'execute', side_effect=IntegrityError("mock", {}, {})):
            with pytest.raises(ValueError, match="Service update failed"):
                repo.update_service("service-id", sample_service)
