#!/usr/bin/env python3
"""
Test script to verify service authorization - only service providers can create/update/delete services
"""
import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:8000"

def test_service_authorization():
    """Test service authorization for different user roles"""
    print("🔐 Testing Service Authorization")
    print("=" * 50)
    
    # Test data
    customer_data = {
        "email": "customer@example.com",
        "password": "customer123456",
        "role": "customer",
        "profile": {
            "firstName": "Customer",
            "lastName": "User",
            "phone": "1234567890",
            "address": "123 Customer St"
        }
    }
    
    provider_data = {
        "email": "provider@example.com",
        "password": "provider123456",
        "role": "service_provider",
        "profile": {
            "firstName": "Service",
            "lastName": "Provider",
            "phone": "0987654321",
            "address": "456 Provider Ave"
        }
    }
    
    service_data = {
        "title": "Test Photography Service",
        "description": "Professional photography session",
        "category": "photography",
        "price": 150.0,
        "currency": "USD",
        "duration": 120,
        "availability": {
            "monday": ["09:00-17:00"],
            "tuesday": ["09:00-17:00"],
            "wednesday": ["09:00-17:00"],
            "thursday": ["09:00-17:00"],
            "friday": ["09:00-17:00"],
            "saturday": [],
            "sunday": []
        },
        "images": ["photo1.jpg", "photo2.jpg"]
    }
    
    print("\n1️⃣  Testing: Unauthenticated Access")
    print("-" * 40)
    
    # Test unauthenticated access
    response = requests.post(f"{BASE_URL}/services/", json=service_data)
    print(f"   POST /services/ (no auth): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Unauthenticated access blocked")
    
    response = requests.put(f"{BASE_URL}/services/test-id", json=service_data)
    print(f"   PUT /services/test-id (no auth): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Unauthenticated update blocked")
    
    response = requests.delete(f"{BASE_URL}/services/test-id")
    print(f"   DELETE /services/test-id (no auth): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Unauthenticated delete blocked")
    
    print("\n2️⃣  Testing: Customer Role Access")
    print("-" * 40)
    
    # Register and login as customer
    response = requests.post(f"{BASE_URL}/users/", json=customer_data)
    print(f"   Register customer: {response.status_code}")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": customer_data["email"],
        "password": customer_data["password"]
    })
    print(f"   Login customer: {response.status_code}")
    customer_token = response.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Test customer trying to create service
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=customer_headers)
    print(f"   POST /services/ (customer): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Customer cannot create services")
    
    # Test customer trying to update service
    response = requests.put(f"{BASE_URL}/services/test-id", json=service_data, headers=customer_headers)
    print(f"   PUT /services/test-id (customer): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Customer cannot update services")
    
    # Test customer trying to delete service
    response = requests.delete(f"{BASE_URL}/services/test-id", headers=customer_headers)
    print(f"   DELETE /services/test-id (customer): {response.status_code}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("   ✅ SUCCESS: Customer cannot delete services")
    
    print("\n3️⃣  Testing: Service Provider Role Access")
    print("-" * 40)
    
    # Register and login as service provider
    response = requests.post(f"{BASE_URL}/users/", json=provider_data)
    print(f"   Register provider: {response.status_code}")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": provider_data["email"],
        "password": provider_data["password"]
    })
    print(f"   Login provider: {response.status_code}")
    provider_token = response.json()["access_token"]
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    
    # Test provider creating service
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=provider_headers)
    print(f"   POST /services/ (provider): {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    print("   ✅ SUCCESS: Provider can create services")
    
    service_id = response.json()["id"]
    print(f"   📝 Created service ID: {service_id}")
    
    # Test provider updating their own service
    updated_service_data = service_data.copy()
    updated_service_data["title"] = "Updated Photography Service"
    response = requests.put(f"{BASE_URL}/services/{service_id}", json=updated_service_data, headers=provider_headers)
    print(f"   PUT /services/{service_id} (provider): {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✅ SUCCESS: Provider can update their own service")
    
    # Test provider deleting their own service
    response = requests.delete(f"{BASE_URL}/services/{service_id}", headers=provider_headers)
    print(f"   DELETE /services/{service_id} (provider): {response.status_code}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"
    print("   ✅ SUCCESS: Provider can delete their own service")
    
    print("\n4️⃣  Testing: Cross-Provider Authorization")
    print("-" * 40)
    
    # Create another provider
    provider2_data = provider_data.copy()
    provider2_data["email"] = "provider2@example.com"
    provider2_data["password"] = "provider2123456"
    provider2_data["profile"]["firstName"] = "Provider2"
    
    response = requests.post(f"{BASE_URL}/users/", json=provider2_data)
    print(f"   Register provider2: {response.status_code}")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": provider2_data["email"],
        "password": provider2_data["password"]
    })
    print(f"   Login provider2: {response.status_code}")
    provider2_token = response.json()["access_token"]
    provider2_headers = {"Authorization": f"Bearer {provider2_token}"}
    
    # Provider1 creates a service
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=provider_headers)
    print(f"   Provider1 creates service: {response.status_code}")
    service_id = response.json()["id"]
    
    # Provider2 tries to update Provider1's service
    response = requests.put(f"{BASE_URL}/services/{service_id}", json=updated_service_data, headers=provider2_headers)
    print(f"   Provider2 updates Provider1's service: {response.status_code}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("   ✅ SUCCESS: Provider cannot update other provider's service")
    
    # Provider2 tries to delete Provider1's service
    response = requests.delete(f"{BASE_URL}/services/{service_id}", headers=provider2_headers)
    print(f"   Provider2 deletes Provider1's service: {response.status_code}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("   ✅ SUCCESS: Provider cannot delete other provider's service")
    
    # Clean up
    requests.delete(f"{BASE_URL}/services/{service_id}", headers=provider_headers)
    
    print("\n5️⃣  Testing: Public Access (GET endpoints)")
    print("-" * 40)
    
    # Test that GET endpoints are still public
    response = requests.get(f"{BASE_URL}/services/")
    print(f"   GET /services/ (no auth): {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✅ SUCCESS: Public can list services")
    
    # Create a service to test individual GET
    response = requests.post(f"{BASE_URL}/services/", json=service_data, headers=provider_headers)
    service_id = response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/services/{service_id}")
    print(f"   GET /services/{service_id} (no auth): {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✅ SUCCESS: Public can view individual service")
    
    # Clean up
    requests.delete(f"{BASE_URL}/services/{service_id}", headers=provider_headers)
    
    print("\n📋 Service Authorization Test Summary:")
    print("=" * 50)
    print("✅ Unauthenticated users cannot create/update/delete services")
    print("✅ Customers cannot create/update/delete services")
    print("✅ Service providers can create services")
    print("✅ Service providers can update their own services")
    print("✅ Service providers can delete their own services")
    print("✅ Service providers cannot modify other providers' services")
    print("✅ Public can still view services (GET endpoints)")
    print("\n🔒 Service authorization is working correctly!")

if __name__ == "__main__":
    test_service_authorization()
