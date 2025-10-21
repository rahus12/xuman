#!/usr/bin/env python3
"""
Test script to verify service ownership authorization
This demonstrates that users can only modify services they own
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def register_user(email, password, role, first_name, last_name):
    """Register a user and return JWT token"""
    user_data = {
        "email": email,
        "password": password,
        "role": role,
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "phone": "+1234567890",
            "address": "123 Test St"
        }
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code in [201, 409]:  # 409 = user already exists
        # Login to get token
        login_data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
    return None

def test_service_ownership():
    """Test that users can only modify services they own"""
    print("🔐 Testing Service Ownership Authorization")
    print("=" * 50)
    
    # Register two service providers
    print("\n1. Registering two service providers...")
    provider1_token = register_user("provider1@example.com", "password123", "provider", "Provider", "One")
    provider2_token = register_user("provider2@example.com", "password123", "provider", "Provider", "Two")
    
    if not provider1_token or not provider2_token:
        print("❌ Failed to register providers")
        return
    
    print("✅ Both providers registered successfully")
    
    # Provider 1 creates a service
    print("\n2. Provider 1 creates a service...")
    headers1 = {"Authorization": f"Bearer {provider1_token}"}
    service_data = {
        "title": "Provider 1's Service",
        "description": "This service belongs to Provider 1",
        "category": "test",
        "price": 50.0,
        "currency": "USD",
        "duration": 60,
        "availability": ["09:00-17:00"],
        "images": []
    }
    
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=headers1)
    if response.status_code == 201:
        service = response.json()
        service_id = service["id"]
        print(f"✅ Provider 1 created service: {service['title']} (ID: {service_id})")
    else:
        print(f"❌ Failed to create service: {response.status_code} - {response.text}")
        return
    
    # Provider 2 tries to update Provider 1's service (should fail)
    print("\n3. Provider 2 tries to update Provider 1's service...")
    headers2 = {"Authorization": f"Bearer {provider2_token}"}
    update_data = {
        "title": "Hacked Service",
        "description": "Provider 2 trying to hijack this service",
        "category": "test",
        "price": 100.0,
        "currency": "USD",
        "duration": 60,
        "availability": ["09:00-17:00"],
        "images": []
    }
    
    response = requests.put(f"{BASE_URL}/services/{service_id}", json=update_data, headers=headers2)
    if response.status_code == 404:
        print("✅ Provider 2 correctly denied access to Provider 1's service")
    else:
        print(f"❌ SECURITY ISSUE: Provider 2 was able to modify Provider 1's service! Status: {response.status_code}")
    
    # Provider 1 updates their own service (should succeed)
    print("\n4. Provider 1 updates their own service...")
    update_data = {
        "title": "Updated Service by Owner",
        "description": "Provider 1 legitimately updating their service",
        "category": "test",
        "price": 75.0,
        "currency": "USD",
        "duration": 60,
        "availability": ["09:00-17:00"],
        "images": []
    }
    
    response = requests.put(f"{BASE_URL}/services/{service_id}", json=update_data, headers=headers1)
    if response.status_code == 200:
        updated_service = response.json()
        print(f"✅ Provider 1 successfully updated their service: {updated_service['title']}")
    else:
        print(f"❌ Provider 1 failed to update their own service: {response.status_code} - {response.text}")
    
    # Provider 2 tries to delete Provider 1's service (should fail)
    print("\n5. Provider 2 tries to delete Provider 1's service...")
    response = requests.delete(f"{BASE_URL}/services/{service_id}", headers=headers2)
    if response.status_code == 404:
        print("✅ Provider 2 correctly denied access to delete Provider 1's service")
    else:
        print(f"❌ SECURITY ISSUE: Provider 2 was able to delete Provider 1's service! Status: {response.status_code}")
    
    # Provider 1 deletes their own service (should succeed)
    print("\n6. Provider 1 deletes their own service...")
    response = requests.delete(f"{BASE_URL}/services/{service_id}", headers=headers1)
    if response.status_code == 204:
        print("✅ Provider 1 successfully deleted their own service")
    else:
        print(f"❌ Provider 1 failed to delete their own service: {response.status_code} - {response.text}")
    
    # Test with a customer trying to access service endpoints
    print("\n7. Customer tries to access service management...")
    customer_token = register_user("customer@example.com", "password123", "customer", "Customer", "User")
    if customer_token:
        headers_customer = {"Authorization": f"Bearer {customer_token}"}
        
        # Customer tries to create a service (should fail - only providers can create)
        service_data = {
            "title": "Customer's Service",
            "description": "Customer trying to create service",
            "category": "test",
            "price": 25.0,
            "currency": "USD",
            "duration": 30,
            "availability": ["09:00-17:00"],
            "images": []
        }
        
        response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=headers_customer)
        if response.status_code == 403:
            print("✅ Customer correctly denied access to create services")
        else:
            print(f"❌ Customer was able to create services! Status: {response.status_code}")
    
    print("\n✅ Service ownership authorization test completed!")

if __name__ == "__main__":
    test_service_ownership()
