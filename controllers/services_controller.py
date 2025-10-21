from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from models import ServiceCreateRequest, ServiceResponse, User, UserRole
from services.services_service import ServicesService
from repositories.services_repository import ServicesRepository
from database import get_db
from auth import get_current_user
from rate_limiter import browsing_rate_limit

router = APIRouter(prefix="/services", tags=["services"])


def get_service_layer(db: Session = Depends(get_db)) -> ServicesService:
    return ServicesService(ServicesRepository(db))


# def require_service_provider(current_user: User = Depends(get_current_user)) -> User:
#     """Require the current user to be a service provider"""
#     if current_user.role != UserRole.SERVICE_PROVIDER:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only service providers can perform this action"
#         )
#     return current_user

# GET all services, anyone can view services
@router.get("/", response_model=List[ServiceResponse])
@browsing_rate_limit()
async def list_services(service: ServicesService = Depends(get_service_layer)):
    return service.list_services()

# Get a specific service, anyone can view services
@router.get("/{service_id}", response_model=ServiceResponse)
@browsing_rate_limit()
async def get_service(service_id: str, service: ServicesService = Depends(get_service_layer)):
    result = service.get_service(service_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return result

# Create a new service, only service providers can create services
@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreateRequest, 
    service: ServicesService = Depends(get_service_layer),
    current_user: User = Depends(get_current_user) # checks if the user is a service provider
):
    """Create a new service - only service providers can create services"""
    # Role validation: only service providers can create services
    if current_user.role != UserRole.SERVICE_PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service providers can create services"
        )
    
    return service.create_service(current_user.email, payload)

# Update a service, only the service owner can update their own service
@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str, 
    payload: ServiceCreateRequest, 
    service: ServicesService = Depends(get_service_layer),
    current_user: User = Depends(get_current_user) # this only checks if the user is authenticated, not whether he is authorized to update this service
):
    """Update a service - only the service owner can update their own service"""
    # Role validation: only service providers can update services
    if current_user.role != UserRole.SERVICE_PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service providers can update services"
        )
    
    result = service.update_service(service_id, payload, current_user.email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Service not found or you don't have permission to update this service"
        )
    return result

# Delete a service, only the service owner can delete their own service
@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str, 
    service: ServicesService = Depends(get_service_layer),
    current_user: User = Depends(get_current_user)
):
    """Delete a service - only the service owner can delete their own service"""
    # Role validation: only service providers can delete services
    if current_user.role != UserRole.SERVICE_PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service providers can delete services"
        )
    
    deleted = service.delete_service(service_id, current_user.email)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Service not found or you don't have permission to delete this service"
        )
    return None