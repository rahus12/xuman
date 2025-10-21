from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from services.email_service import EmailService
from database import get_db

router = APIRouter(prefix="/emails", tags=["email-notifications"])


def get_email_service() -> EmailService:
    return EmailService()


@router.get("/history")
async def get_email_history(
    user_email: Optional[str] = Query(None),
    service: EmailService = Depends(get_email_service)
):
    """Get email notification history (for testing/debugging)"""
    emails = service.get_email_history(user_email)
    return {
        "count": len(emails),
        "emails": emails
    }


@router.get("/test")
async def test_email_service(service: EmailService = Depends(get_email_service)):
    """Test email service functionality"""
    from models import User, UserProfile, Service, ServiceAvailability, Booking, BookingStatus
    from datetime import datetime, timezone
    
    # Create test data
    customer = User(
        id="test-customer-id",
        email="customer@test.com",
        password="hashed",
        role="customer",
        profile=UserProfile(
            firstName="John",
            lastName="Doe",
            phone="+1234567890",
            address="123 Test St"
        )
    )
    
    provider = User(
        id="test-provider-id",
        email="provider@test.com",
        password="hashed",
        role="provider",
        profile=UserProfile(
            firstName="Jane",
            lastName="Smith",
            phone="+0987654321",
            address="456 Provider Ave"
        )
    )
    
    service_obj = Service(
        id="test-service-id",
        providerId="provider@test.com",
        title="Test Service",
        description="A test service for email notifications",
        category="test",
        price=50.0,
        currency="USD",
        duration=60,
        availability=ServiceAvailability(monday=["09:00", "17:00"]),
        images=[]
    )
    
    booking = Booking(
        id="test-booking-id",
        customerId="customer@test.com",
        serviceId="test-service-id",
        providerId="provider@test.com",
        status=BookingStatus.PENDING,
        scheduledAt=datetime.now(timezone.utc),
        duration=60,
        totalAmount=50.0,
        notes="Test booking"
    )
    
    # Send test emails
    try:
        confirmation_path = service.send_booking_confirmation(customer, provider, service_obj, booking)
        provider_notification_path = service.send_booking_notification_to_provider(customer, provider, service_obj, booking)
        update_path = service.send_booking_update(customer, provider, service_obj, booking, BookingStatus.PENDING)
        
        return {
            "message": "Test emails sent successfully",
            "files": {
                "confirmation": confirmation_path,
                "provider_notification": provider_notification_path,
                "update_notification": update_path
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email test failed: {str(e)}")
