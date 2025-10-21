#!/usr/bin/env python3
"""
Test script for Server-Sent Events (SSE) notifications
This script demonstrates real-time notifications functionality
"""

import requests
import json
import time
import threading
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_sse_connection():
    """Test SSE connection and receive notifications"""
    print("🔌 Testing SSE connection...")
    
    # First, we need to register a user and get a JWT token
    print("\n1. Registering test user...")
    user_data = {
        "email": "sse_test@example.com",
        "password": "testpassword123",
        "role": "customer",
        "profile": {
            "firstName": "SSE",
            "lastName": "Test",
            "phone": "+1234567890",
            "address": "123 Test St"
        }
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        print("✅ User registered successfully")
    elif response.status_code == 409:
        print("ℹ️ User already exists, continuing...")
    else:
        print(f"❌ Failed to register user: {response.status_code} - {response.text}")
        return
    
    # Login to get JWT token
    print("\n2. Logging in...")
    login_data = {
        "email": "sse_test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
    else:
        print(f"❌ Failed to login: {response.status_code} - {response.text}")
        return
    
    # Set up headers with JWT token
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream"
    }
    
    print("\n3. Connecting to SSE stream...")
    print("📡 Listening for real-time notifications...")
    print("   (This will run for 30 seconds to demonstrate SSE)")
    print("   Open another terminal and run: python test_notification_trigger.py")
    print("   to trigger some notifications\n")
    
    try:
        # Connect to SSE endpoint
        response = requests.get(
            f"{BASE_URL}/notifications/stream",
            headers=headers,
            stream=True,
            timeout=35
        )
        
        if response.status_code == 200:
            print("✅ SSE connection established!")
            print("📨 Waiting for notifications...\n")
            
            # Read SSE stream
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            
                            if data.get("type") == "ping":
                                print(f"[{timestamp}] 💓 Keep-alive ping")
                            else:
                                print(f"[{timestamp}] 🔔 Notification received:")
                                print(f"   Title: {data.get('title', 'N/A')}")
                                print(f"   Message: {data.get('message', 'N/A')}")
                                print(f"   Type: {data.get('type', 'N/A')}")
                                if data.get('data'):
                                    print(f"   Data: {json.dumps(data['data'], indent=2)}")
                                print()
                        except json.JSONDecodeError:
                            print(f"[{timestamp}] 📄 Raw data: {line}")
                    else:
                        print(f"📄 Raw line: {line}")
        else:
            print(f"❌ Failed to connect to SSE: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏰ SSE connection timeout (30 seconds)")
    except KeyboardInterrupt:
        print("\n🛑 SSE connection interrupted by user")
    except Exception as e:
        print(f"❌ Error in SSE connection: {e}")

def test_notification_endpoints():
    """Test notification REST endpoints"""
    print("\n🔧 Testing notification REST endpoints...")
    
    # Login first
    login_data = {
        "email": "sse_test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Failed to login for endpoint testing")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get notifications
    print("\n1. Getting notifications...")
    response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
    if response.status_code == 200:
        notifications = response.json()
        print(f"✅ Found {len(notifications)} notifications")
        for notif in notifications[:3]:  # Show first 3
            print(f"   - {notif['title']}: {notif['message']}")
    else:
        print(f"❌ Failed to get notifications: {response.status_code}")
    
    # Test get notification count
    print("\n2. Getting notification count...")
    response = requests.get(f"{BASE_URL}/notifications/count", headers=headers)
    if response.status_code == 200:
        count = response.json()
        print(f"✅ Total: {count['total']}, Unread: {count['unread']}")
    else:
        print(f"❌ Failed to get count: {response.status_code}")
    
    # Test create notification (for testing)
    print("\n3. Creating test notification...")
    test_notification = {
        "userId": "sse_test@example.com",
        "type": "BOOKING_CREATED",
        "title": "Test Notification",
        "message": "This is a test notification created via API",
        "data": {"test": True, "timestamp": datetime.now().isoformat()}
    }
    
    response = requests.post(f"{BASE_URL}/notifications/", json=test_notification, headers=headers)
    if response.status_code == 200:
        print("✅ Test notification created successfully")
    else:
        print(f"❌ Failed to create notification: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🚀 SSE Notifications Test")
    print("=" * 50)
    
    # Test notification endpoints first
    test_notification_endpoints()
    
    # Then test SSE connection
    test_sse_connection()
    
    print("\n✅ SSE notifications test completed!")
