#!/usr/bin/env python3
"""
Test refund functionality
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_refund():
    print("🧪 Testing Refund")
    print("=" * 30)
    
    # First create a payment
    payment_data = {
        "bookingId": str(uuid.uuid4()),
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
    
    print("Creating payment...")
    response = requests.post(f"{BASE_URL}/payments/process", json=payment_data)
    print(f"Payment Status: {response.status_code}")
    
    if response.status_code == 201:
        payment = response.json()
        print(f"Payment ID: {payment['id']}")
        print(f"Payment Status: {payment['status']}")
        
        # Now test refund
        refund_data = {
            "paymentId": payment['id'],
            "reason": "Test refund"
        }
        
        print("\nTesting refund...")
        refund_response = requests.post(f"{BASE_URL}/payments/refund", json=refund_data)
        print(f"Refund Status: {refund_response.status_code}")
        print(f"Refund Response: {refund_response.text}")
        
    else:
        print(f"Payment failed: {response.text}")

if __name__ == "__main__":
    test_refund()
