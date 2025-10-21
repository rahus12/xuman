#!/usr/bin/env python3
"""
Test script to demonstrate the payment flow
"""
import requests
import json
import random

BASE_URL = "http://localhost:8000"

def test_payment_flow():
    print("🧪 Testing Payment Flow")
    print("=" * 50)
    
    # 1. First, let's create a service to book
    print("\n1. Creating a test service...")
    service_data = {
        "title": "Test Service",
        "description": "A test service for payment testing",
        "category": "consulting",
        "price": 100.0,
        "currency": "USD",
        "duration": 60,
        "availability": {
            "monday": ["09:00-17:00"],
            "tuesday": ["09:00-17:00"],
            "wednesday": ["09:00-17:00"],
            "thursday": ["09:00-17:00"],
            "friday": ["09:00-17:00"],
            "saturday": [],
            "sunday": []
        },
        "images": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/services/?providerId=provider@test.com", json=service_data)
        if response.status_code == 201:
            service = response.json()
            service_id = service["id"]
            print(f"✅ Service created with ID: {service_id}")
        else:
            print(f"❌ Failed to create service: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        return
    
    # 2. Test payment processing (multiple attempts to see 10% failure rate)
    print("\n2. Testing payment processing (10% failure rate)...")
    
    success_count = 0
    failure_count = 0
    
    for i in range(10):
        print(f"\n--- Payment Attempt {i+1} ---")
        
        payment_data = {
            "bookingId": service_id,  # Using service_id as bookingId for this test
            "amount": 100.0,
            "currency": "USD",
            "paymentMethod": {
                "type": "card",
                "cardNumber": f"411111111111111{i}",  # Test card numbers
                "expiryMonth": 12,
                "expiryYear": 2025,
                "cvv": "123",
                "cardholderName": f"Test User {i+1}"
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/bookings/with-payment", json=payment_data)
            
            if response.status_code == 201:
                booking = response.json()
                print(f"✅ Payment SUCCESS - Booking created: {booking['id']}")
                success_count += 1
            elif response.status_code == 400:
                print(f"❌ Payment FAILED - Booking not created")
                failure_count += 1
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error processing payment: {e}")
            failure_count += 1
    
    # 3. Summary
    print(f"\n📊 Payment Test Results:")
    print(f"   Successes: {success_count}")
    print(f"   Failures: {failure_count}")
    print(f"   Success Rate: {(success_count/(success_count+failure_count)*100):.1f}%")
    
    # 4. Test individual payment endpoints
    print(f"\n3. Testing individual payment endpoints...")
    
    # Test payment processing directly
    payment_data = {
        "bookingId": service_id,
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
    
    try:
        response = requests.post(f"{BASE_URL}/payments/process", json=payment_data)
        if response.status_code in [201, 402]:  # 201 for success, 402 for payment required (failure)
            payment = response.json()
            print(f"✅ Direct payment processed: {payment['status']}")
            
            if payment['status'] == 'completed':
                # Test refund
                refund_data = {
                    "paymentId": payment['id'],
                    "reason": "Test refund"
                }
                
                refund_response = requests.post(f"{BASE_URL}/payments/refund", json=refund_data)
                if refund_response.status_code == 201:
                    refund = refund_response.json()
                    print(f"✅ Refund processed: {refund['status']}")
                else:
                    print(f"❌ Refund failed: {refund_response.status_code}")
        else:
            print(f"❌ Direct payment failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing direct payment: {e}")

if __name__ == "__main__":
    test_payment_flow()
