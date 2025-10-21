from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    PROVIDER = "PROVIDER"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserProfile(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=1, max_length=200)


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    profile: UserProfile
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ServiceAvailability(BaseModel):
    monday: Optional[List[str]] = None
    tuesday: Optional[List[str]] = None
    wednesday: Optional[List[str]] = None
    thursday: Optional[List[str]] = None
    friday: Optional[List[str]] = None
    saturday: Optional[List[str]] = None
    sunday: Optional[List[str]] = None


class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    providerId: str
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    duration: int = Field(..., gt=0, description="Duration in minutes")
    availability: ServiceAvailability
    images: List[str] = Field(default_factory=list)
    isActive: bool = Field(default=True)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customerId: str
    serviceId: str
    providerId: str
    status: BookingStatus = BookingStatus.PENDING
    scheduledAt: datetime
    duration: int = Field(..., gt=0, description="Duration in minutes")
    totalAmount: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response Models for API endpoints

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    profile: UserProfile


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    profile: UserProfile
    createdAt: datetime
    updatedAt: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ServiceCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    duration: int = Field(..., gt=0, description="Duration in minutes")
    availability: ServiceAvailability
    images: List[str] = Field(default_factory=list)


class ServiceResponse(BaseModel):
    id: str
    providerId: str
    title: str
    description: str
    category: str
    price: float
    currency: str
    duration: int
    availability: ServiceAvailability
    images: List[str]
    isActive: bool
    createdAt: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BookingCreateRequest(BaseModel):
    serviceId: str
    scheduledAt: datetime
    notes: Optional[str] = Field(None, max_length=500)
    payment: PaymentRequest


class BookingResponse(BaseModel):
    id: str
    customerId: str
    serviceId: str
    providerId: str
    status: BookingStatus
    scheduledAt: datetime
    duration: int
    totalAmount: float
    notes: Optional[str]
    createdAt: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BookingUpdateRequest(BaseModel):
    status: Optional[BookingStatus] = None
    scheduledAt: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


# Authentication Models

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordResetToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    token: str
    expiresAt: datetime
    isUsed: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Payment Models
class PaymentMethod(BaseModel):
    type: str = "card"  # Only card payments
    cardNumber: str = Field(..., min_length=16, max_length=19)
    expiryMonth: int = Field(..., ge=1, le=12)
    expiryYear: int = Field(..., ge=2024)
    cvv: str = Field(..., min_length=3, max_length=4)
    cardholderName: str = Field(..., min_length=2, max_length=100)


class PaymentRequest(BaseModel):
    bookingId: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    paymentMethod: PaymentMethod


class PaymentResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bookingId: str
    status: str  # "pending", "completed", "failed", "refunded"
    transactionId: str = Field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:12]}")
    amount: float
    currency: str
    paymentMethod: PaymentMethod
    failureReason: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RefundRequest(BaseModel):
    paymentId: str
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    paymentId: str
    status: str  # "pending", "completed", "failed"
    amount: float
    reason: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationType(str, Enum):
    BOOKING_CREATED = "booking_created"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_CANCELLED = "booking_cancelled"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    REFUND_PROCESSED = "refund_processed"
    SERVICE_CREATED = "service_created"
    SERVICE_UPDATED = "service_updated"
    SERVICE_DELETED = "service_deleted"
    PASSWORD_RESET = "password_reset"
    PASSWORD_RESET_CONFIRMED = "password_reset_confirmed"


class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    isRead: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    readAt: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationCreateRequest(BaseModel):
    userId: str
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: str
    userId: str
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    isRead: bool
    createdAt: datetime
    readAt: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
