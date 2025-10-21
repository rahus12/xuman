#!/usr/bin/env python3
"""
Script to trigger notifications for testing SSE functionality
Run this while test_sse_notifications.py is running to see real-time notifications
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def register_and_login():
    """Register a user and login to get JWT token"""
    # Register user
    user_data = {
        "email": "trigger_test@example.com",
        "password": "testpassword123",
        "role": "customer",
        "profile": {
            "firstName": "Trigger",
            "lastName": "Test",
            "phone": "+1234567890",
            "address": "123 Trigger St"
        }
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code not in [201, 409]:
        print(f"❌ Failed to register user: {response.status_code}")
        return None
    
    # Login
    login_data = {
        "email": "trigger_test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to login: {response.status_code}")
        return None

def create_test_service(token):
    """Create a test service"""
    headers = {"Authorization": f"Bearer {token}"}
    
    service_data = {
        "title": "Test Service for Notifications",
        "description": "A service to test notification functionality",
        "category": "test",
        "price": 25.0,
        "currency": "USD",
        "duration": 60,
        "availability": ["09:00-17:00"],
        "images": []
    }
    
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=headers)
    if response.status_code == 201:
        service = response.json()
        print(f"✅ Created service: {service['title']} (ID: {service['id']})")
        return service
    else:
        print(f"❌ Failed to create service: {response.status_code} - {response.text}")
        return None

def create_test_booking(token, service_id):
    """Create a test booking to trigger notifications"""
    headers = {"Authorization": f"Bearer {token}"}
    
    booking_data = {
        "serviceId": service_id,
        "scheduledAt": (datetime.now() + timedelta(days=1)).isoformat(),
        "notes": "Test booking for notification testing",
        "payment": {
            "bookingId": str(uuid.uuid4()),
            "amount": 25.0,
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
    }
    
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
    if response.status_code == 201:
        booking = response.json()
        print(f"✅ Created booking: {booking['id']}")
        return booking
    else:
        print(f"❌ Failed to create booking: {response.status_code} - {response.text}")
        return None

def create_direct_notification(token):
    """Create a notification directly via API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    notification_data = {
        "userId": "sse_test@example.com",  # Send to the SSE test user
        "type": "BOOKING_CREATED",
        "title": "Direct API Notification",
        "message": f"This notification was created directly via API at {datetime.now().strftime('%H:%M:%S')}",
        "data": {
            "source": "direct_api",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/notifications/", json=notification_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Created direct notification")
        return True
    else:
        print(f"❌ Failed to create direct notification: {response.status_code} - {response.text}")
        return False

def trigger_payment_notifications(token):
    """Trigger payment notifications"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n💳 Testing payment notifications...")
    
    # Create multiple payment requests to test success/failure notifications
    for i in range(5):
        payment_data = {
            "bookingId": str(uuid.uuid4()),
            "amount": 50.0 + (i * 10),
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
        
        response = requests.post(f"{BASE_URL}/payments/process", json=payment_data, headers=headers)
        if response.status_code in [201, 402]:  # 402 = Payment Required (failed)
            result = response.json()
            print(f"   Payment {i+1}: {result['status']} - ${payment_data['amount']}")
        else:
            print(f"   Payment {i+1}: Failed to process - {response.status_code}")
        
        time.sleep(1)  # Small delay between payments

def main():
    print("🎯 Notification Trigger Test")
    print("=" * 40)
    
    # Get authentication token
    token = register_and_login()
    if not token:
        return
    
    print(f"✅ Authenticated as trigger_test@example.com")
    
    # Create a service
    print("\n🏗️ Creating test service...")
    service = create_test_service(token)
    if not service:
        return
    
    # Create direct notifications
    print("\n📨 Creating direct notifications...")
    for i in range(3):
        create_direct_notification(token)
        time.sleep(2)
    
    # Create a booking (this will trigger booking notifications)
    print("\n📅 Creating test booking...")
    booking = create_test_booking(token, service['id'])
    if booking:
        print("   This should trigger booking notifications for both customer and provider")
    
    # Trigger payment notifications
    trigger_payment_notifications(token)
    
    print("\n✅ Notification trigger test completed!")
    print("   Check the SSE connection in the other terminal to see real-time notifications")

if __name__ == "__main__":
    main()
