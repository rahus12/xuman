#!/usr/bin/env python3
"""
Debug payment service directly
"""
import sys
sys.path.append('.')

from services.payments_service import PaymentsService
from repositories.payments_repository import PaymentsRepository
from database import SessionLocal
from models import PaymentRequest, PaymentMethod

def test_payment_service():
    print("🔍 Debugging Payment Service")
    print("=" * 40)
    
    try:
        # Create database session
        db = SessionLocal()
        payments_repo = PaymentsRepository(db)
        payments_service = PaymentsService(payments_repo)
        
        # Create payment request
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123",
            cardholderName="Test User"
        )
        
        import uuid
        payment_request = PaymentRequest(
            bookingId=str(uuid.uuid4()),
            amount=50.0,
            currency="USD",
            paymentMethod=payment_method
        )
        
        print("Processing payment...")
        payment = payments_service.process_payment(payment_request)
        print(f"Payment result: {payment.status}")
        print(f"Payment ID: {payment.id}")
        print(f"Transaction ID: {payment.transactionId}")
        
        if payment.failureReason:
            print(f"Failure reason: {payment.failureReason}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_payment_service()
