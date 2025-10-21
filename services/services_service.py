from typing import List, Optional

from models import Service, ServiceCreateRequest, ServiceResponse
from repositories.services_repository import ServicesRepository


class ServicesService:
    def __init__(self, repository: ServicesRepository) -> None:
        self.repository = repository

    def list_services(self) -> List[ServiceResponse]:
        return [self._to_response(s) for s in self.repository.list_services()]

    def get_service(self, service_id: str) -> Optional[ServiceResponse]:
        service = self.repository.get_service(service_id)
        return self._to_response(service) if service else None

    # provider id is the email of the service provider
    def create_service(self, provider_email: str, payload: ServiceCreateRequest) -> ServiceResponse:
        # Note: Role validation should be done in controller layer
        # Service layer focuses on business logic and ownership validation
        
        service = Service(
            providerId=provider_email,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            price=payload.price,
            currency=payload.currency,
            duration=payload.duration,
            availability=payload.availability,
            images=payload.images,
        )
        created = self.repository.create_service(service)
        return self._to_response(created)

    def update_service(self, service_id: str, payload: ServiceCreateRequest, current_user_email: str) -> Optional[ServiceResponse]:
        """Update a service with authorization check - only the service provider can update"""
        # Note: Role validation should be done in controller layer
        # Service layer focuses on business logic and ownership validation
        
        existing = self.repository.get_service(service_id)
        if not existing:
            return None
        
        # Authorization check: only the service provider can update their own service
        if existing.providerId != current_user_email:
            return None  # Service layer returns None for unauthorized access
        
        updated = Service(
            id=existing.id,
            providerId=existing.providerId,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            price=payload.price,
            currency=payload.currency,
            duration=payload.duration,
            availability=payload.availability,
            images=payload.images,
            isActive=existing.isActive,
            createdAt=existing.createdAt,
        )
        saved = self.repository.update_service(service_id, updated)
        return self._to_response(saved) if saved else None


    # do we need to check if people have already booked this service?
    def delete_service(self, service_id: str, current_user_email: str) -> bool:
        """Delete a service with authorization check - only the service provider can delete"""
        # Note: Role validation should be done in controller layer
        # Service layer focuses on business logic and ownership validation
        
        existing = self.repository.get_service(service_id)
        if not existing:
            return False
        
        # Authorization check: only the service provider can delete their own service
        if existing.providerId != current_user_email:
            return False  # Service layer returns False for unauthorized access
        
        return self.repository.delete_service(service_id)

    def _to_response(self, s: Service) -> ServiceResponse:
        return ServiceResponse(
            id=s.id,
            providerId=s.providerId,
            title=s.title,
            description=s.description,
            category=s.category,
            price=s.price,
            currency=s.currency,
            duration=s.duration,
            availability=s.availability,
            images=s.images,
            isActive=s.isActive,
            createdAt=s.createdAt,
        )


