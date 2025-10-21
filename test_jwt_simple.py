#!/usr/bin/env python3
"""
Simple test to verify JWT authentication is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_jwt_simple():
    print("🔐 Simple JWT Authentication Test")
    print("=" * 40)
    
    # Test 1: Access protected endpoint without JWT
    print("\n1. Testing access to protected endpoint without JWT...")
    try:
        response = requests.get(f"{BASE_URL}/bookings/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ CORRECT: 401 Unauthorized (JWT required)")
        else:
            print(f"   ❌ UNEXPECTED: Expected 401, got {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Access protected endpoint with invalid JWT
    print("\n2. Testing access with invalid JWT...")
    headers = {"Authorization": "Bearer invalid-token"}
    try:
        response = requests.get(f"{BASE_URL}/bookings/", headers=headers)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ CORRECT: 401 Unauthorized (Invalid JWT)")
        else:
            print(f"   ❌ UNEXPECTED: Expected 401, got {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check if auth endpoints are working
    print("\n3. Testing auth endpoints...")
    try:
        # Test login with invalid credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Login Status Code: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ CORRECT: 401 Unauthorized (Invalid credentials)")
        else:
            print(f"   ❌ UNEXPECTED: Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check health endpoint (should work without auth)
    print("\n4. Testing public endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ CORRECT: 200 OK (Public endpoint works)")
        else:
            print(f"   ❌ UNEXPECTED: Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_jwt_simple()
