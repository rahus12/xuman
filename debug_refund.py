#!/usr/bin/env python3
"""
Debug refund service directly
"""
import sys
sys.path.append('.')

from services.payments_service import PaymentsService
from repositories.payments_repository import PaymentsRepository
from database import SessionLocal
from models import PaymentRequest, PaymentMethod
import uuid

def test_refund_service():
    print("🔍 Debugging Refund Service")
    print("=" * 40)
    
    try:
        # Create database session
        db = SessionLocal()
        payments_repo = PaymentsRepository(db)
        payments_service = PaymentsService(payments_repo)
        
        # Create payment first
        payment_method = PaymentMethod(
            type="card",
            cardNumber="4111111111111111",
            expiryMonth=12,
            expiryYear=2025,
            cvv="123",
            cardholderName="Test User"
        )
        
        payment_request = PaymentRequest(
            bookingId=str(uuid.uuid4()),
            amount=50.0,
            currency="USD",
            paymentMethod=payment_method
        )
        
        print("Creating payment...")
        payment = payments_service.process_payment(payment_request)
        print(f"Payment created: {payment.id}, Status: {payment.status}")
        
        # Now test refund
        print("Testing refund...")
        refund = payments_service.process_refund(payment.id, "Test refund")
        
        if refund:
            print(f"Refund created: {refund.id}, Status: {refund.status}")
        else:
            print("Refund failed - returned None")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refund_service()
