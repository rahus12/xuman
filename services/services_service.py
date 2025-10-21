from typing import List, Optional
from datetime import datetime, timezone

from models import Service, ServiceCreateRequest, ServiceResponse
from repositories.services_repository import ServicesRepository
from repositories.users_repository import UsersRepository


class ServicesService:
    def __init__(self, repository: ServicesRepository, users_repository: UsersRepository = None) -> None:
        self.repository = repository
        self.users_repository = users_repository

    def list_services(self) -> List[ServiceResponse]:
        return [self._to_response(s) for s in self.repository.list_services()]

    def get_service(self, service_id: str) -> Optional[ServiceResponse]:
        service = self.repository.get_service(service_id)
        return self._to_response(service) if service else None

    # provider id is the email of the service provider
    def create_service(self, provider_email: str, payload: ServiceCreateRequest) -> ServiceResponse:
        # Note: Role validation should be done in controller layer
        # Service layer focuses on business logic and ownership validation
        
        # Get provider's UUID from email
        if self.users_repository:
            provider = self.users_repository.get_by_email(provider_email)
            if not provider:
                raise ValueError(f"Provider with email {provider_email} not found")
            provider_id = provider.id
        else:
            # Fallback: assume provider_email is the ID (should not happen in production)
            provider_id = provider_email
        
        service = Service(
            providerId=provider_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            durationMinutes=payload.durationMinutes,
            availability=payload.availability,
            status="PENDING"
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
        
        # Get current user's UUID from email
        if self.users_repository:
            current_user = self.users_repository.get_by_email(current_user_email)
            if not current_user:
                return None
            current_user_id = current_user.id
        else:
            current_user_id = current_user_email
        
        # Authorization check: only the service provider can update their own service
        if existing.providerId != current_user_id:
            return None  # Service layer returns None for unauthorized access
        
        updated = Service(
            id=existing.id,
            providerId=existing.providerId,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            durationMinutes=payload.durationMinutes,
            availability=payload.availability,
            status=existing.status,
            createdAt=existing.createdAt,
            updatedAt=datetime.now(timezone.utc)
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
        
        # Get current user's UUID from email
        if self.users_repository:
            current_user = self.users_repository.get_by_email(current_user_email)
            if not current_user:
                return False
            current_user_id = current_user.id
        else:
            current_user_id = current_user_email
        
        # Authorization check: only the service provider can delete their own service
        if existing.providerId != current_user_id:
            return False  # Service layer returns False for unauthorized access
        
        return self.repository.delete_service(service_id)

    def _to_response(self, s: Service) -> ServiceResponse:
        return ServiceResponse(
            id=s.id,
            providerId=s.providerId,
            name=s.name,
            description=s.description,
            price=s.price,
            durationMinutes=s.durationMinutes,
            availability=s.availability,
            status=s.status,
            createdAt=s.createdAt,
            updatedAt=s.updatedAt
        )


