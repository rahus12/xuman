from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import PaymentRequest, PaymentResponse, RefundRequest, RefundResponse
from services.payments_service import PaymentsService
from repositories.payments_repository import PaymentsRepository
from database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payments_service(db: Session = Depends(get_db)) -> PaymentsService:
    return PaymentsService(PaymentsRepository(db))


@router.post("/process", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payment_request: PaymentRequest,
    service: PaymentsService = Depends(get_payments_service)
):
    """Process a payment for a booking"""
    # Validate payment method
    is_valid, error_message = service.validate_payment_method(payment_request.paymentMethod)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Process payment
    payment = service.process_payment(payment_request)
    
    if payment.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Payment failed",
                "failure_reason": payment.failureReason,
                "payment_id": payment.id
            }
        )

    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    service: PaymentsService = Depends(get_payments_service)
):
    """Get payment status by ID"""
    payment = service.get_payment_status(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.get("/booking/{booking_id}", response_model=PaymentResponse)
async def get_payment_by_booking(
    booking_id: str,
    service: PaymentsService = Depends(get_payments_service)
):
    """Get payment by booking ID"""
    payment = service.get_payment_by_booking(booking_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this booking"
        )
    return payment


@router.post("/refund", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def process_refund(
    refund_request: RefundRequest,
    service: PaymentsService = Depends(get_payments_service)
):
    """Process a refund for a payment"""
    refund = service.process_refund(refund_request.paymentId, refund_request.reason)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund not possible. Payment not found or not eligible for refund."
        )
    return refund


@router.get("/{payment_id}/refunds", response_model=List[RefundResponse])
async def get_refunds(
    payment_id: str,
    service: PaymentsService = Depends(get_payments_service)
):
    """Get all refunds for a payment"""
    refunds = service.get_refunds(payment_id)
    return refunds
