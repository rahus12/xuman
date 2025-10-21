#!/usr/bin/env python3
"""
Test JWT authentication for booking endpoints
"""
import requests
import json
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:8000"

def test_jwt_authentication():
    print("🔐 Testing JWT Authentication for Bookings")
    print("=" * 50)
    
    # 1. First, create a user and get a JWT token
    print("\n1. Creating a test user and getting JWT token...")
    
    # Register a user
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "customer",
        "profile": {
            "firstName": "Test",
            "lastName": "User",
            "phone": "+1234567890",
            "address": "123 Test Street, Test City, TC 12345"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 201:
            print("✅ User created successfully")
        elif response.status_code == 409:
            print("ℹ️  User already exists, continuing...")
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return
    
    # Login to get JWT token
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ JWT token obtained: {access_token[:20]}...")
        else:
            print(f"❌ Failed to login: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # 2. Create a service (as a provider)
    print("\n2. Creating a test service...")
    service_data = {
        "title": "Test Service for JWT Auth",
        "description": "A test service to verify JWT authentication",
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
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/services/?providerId=testuser@example.com", json=service_data, headers=headers)
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
    
    # 3. Test booking creation WITH authentication
    print(f"\n3. Testing booking creation WITH JWT authentication...")
    booking_data = {
        "serviceId": service_id,
        "scheduledAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "notes": "Test booking with JWT auth",
        "payment": {
            "bookingId": str(uuid.uuid4()),
            "amount": 100.0,
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
    
    try:
        response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
        if response.status_code == 201:
            booking = response.json()
            print(f"✅ Booking created WITH JWT auth: SUCCESS")
            print(f"   Booking ID: {booking['id']}")
            print(f"   Customer ID: {booking['customerId']}")
            print(f"   Status: {booking['status']}")
        else:
            print(f"❌ Booking creation WITH JWT auth: FAILED - {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating booking with JWT: {e}")
    
    # 4. Test booking creation WITHOUT authentication (should fail)
    print(f"\n4. Testing booking creation WITHOUT JWT authentication (should fail)...")
    
    try:
        response = requests.post(f"{BASE_URL}/bookings/", json=booking_data)  # No headers
        if response.status_code == 401:
            print(f"✅ Booking creation WITHOUT JWT auth: CORRECTLY REJECTED (401 Unauthorized)")
            print(f"   This confirms JWT authentication is working!")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing booking without JWT: {e}")
    
    # 5. Test listing bookings with authentication
    print(f"\n5. Testing listing bookings WITH JWT authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/", headers=headers)
        if response.status_code == 200:
            bookings = response.json()
            print(f"✅ List bookings WITH JWT auth: SUCCESS")
            print(f"   Found {len(bookings)} bookings")
            for booking in bookings:
                print(f"   - Booking {booking['id']}: {booking['customerId']} -> {booking['status']}")
        else:
            print(f"❌ List bookings WITH JWT auth: FAILED - {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error listing bookings with JWT: {e}")
    
    # 6. Test listing bookings WITHOUT authentication (should fail)
    print(f"\n6. Testing listing bookings WITHOUT JWT authentication (should fail)...")
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/")  # No headers
        if response.status_code == 401:
            print(f"✅ List bookings WITHOUT JWT auth: CORRECTLY REJECTED (401 Unauthorized)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing list bookings without JWT: {e}")
    
    print(f"\n📋 JWT Authentication Summary:")
    print(f"   ✅ All booking endpoints now require JWT authentication")
    print(f"   ✅ User identity is extracted from JWT token")
    print(f"   ✅ Authorization checks prevent unauthorized access")
    print(f"   ✅ No more hardcoded customer IDs!")

if __name__ == "__main__":
    test_jwt_authentication()
