#!/usr/bin/env python3
"""
Simple payment test without service creation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_payment_directly():
    print("🧪 Testing Payment Directly")
    print("=" * 40)
    
    # Test payment processing directly
    import uuid
    payment_data = {
        "bookingId": str(uuid.uuid4()),  # Use a proper UUID
        "amount": 50.0,
        "currency": "USD",
        "paymentMethod": {
            "type": "card",
            "cardNumber": "4111111111111111",
            "expiryMonth": 12,
            "expiryYear": 2025,
            "cvv": "123",
            "cardholderName": "Test User"
        }
    }
    
    print("Testing direct payment processing...")
    try:
        response = requests.post(f"{BASE_URL}/payments/process", json=payment_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [201, 402]:  # 201 for success, 402 for payment required (failure)
            payment = response.json()
            print(f"✅ Payment processed: {payment['status']}")
            
            if payment['status'] == 'completed':
                # Test refund
                print("\nTesting refund...")
                refund_data = {
                    "paymentId": payment['id'],
                    "reason": "Test refund"
                }
                
                refund_response = requests.post(f"{BASE_URL}/payments/refund", json=refund_data)
                print(f"Refund Status Code: {refund_response.status_code}")
                print(f"Refund Response: {refund_response.text}")
                
                if refund_response.status_code == 201:
                    refund = refund_response.json()
                    print(f"✅ Refund processed: {refund['status']}")
                else:
                    print(f"❌ Refund failed")
        else:
            print(f"❌ Payment failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_payment_directly()
