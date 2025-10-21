from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models import BookingCreateRequest, BookingResponse, BookingUpdateRequest, PaymentRequest, User
from auth import get_current_user
from repositories.bookings_repository import BookingsRepository
from repositories.services_repository import ServicesRepository
from repositories.users_repository import UsersRepository
from services.bookings_service import BookingsService
from database import get_db

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_booking_layer(db: Session = Depends(get_db)) -> BookingsService:
    return BookingsService(BookingsRepository(db), ServicesRepository(db), UsersRepository(db))


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    customerId: Optional[str] = Query(None),
    providerId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_booking_layer),
):
    # If no customerId provided, use current user's email
    if not customerId:
        customerId = current_user.email
    return service.list_bookings(customer_id=customerId, provider_id=providerId)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str, 
    current_user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_booking_layer)
):
    result = service.get_booking(booking_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Check if user has access to this booking (either customer or provider)
    if result.customerId != current_user.email and result.providerId != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to access this booking"
        )
    
    return result

'''
body example: {
    "serviceId": "service-uuid",
    "scheduledAt": "2024-01-15T10:00:00Z",
    "notes": "Please clean the kitchen thoroughly"
  }'
'''
@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreateRequest, 
    current_user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_booking_layer)
):
    """Create a booking with mandatory payment processing - payment must succeed before booking is created"""
    result = service.create_booking(current_user.email, payload)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Booking creation failed. Payment may have failed or service not found."
        )
    return result


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str, 
    payload: BookingUpdateRequest, 
    current_user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_booking_layer)
):
    """Update a booking - authorization handled in service layer"""
    result = service.update_booking(booking_id, payload, current_user.email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found or you don't have permission to update this booking"
        )
    return result


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str, 
    current_user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_booking_layer)
):
    """Delete a booking - authorization handled in service layer"""
    deleted = service.delete_booking(booking_id, current_user.email)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found or you don't have permission to delete this booking"
        )
    return None

