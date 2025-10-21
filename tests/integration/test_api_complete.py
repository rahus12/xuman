"""
Integration tests for complete API flows
Tests end-to-end scenarios through HTTP API
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    def test_register_new_consumer(self, client):
        """Test registering a new consumer user"""
        response = client.post("/users/", json={
            "email": "newconsumer@example.com",
            "password": "password123",
            "role": "CUSTOMER",
            "profile": {
                "firstName": "New",
                "lastName": "Consumer",
                "phone": "+1234567890",
                "address": "123 Test St"
            }
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newconsumer@example.com"
        assert data["role"] == "CUSTOMER"
    
    def test_register_new_provider(self, client):
        """Test registering a new provider user"""
        response = client.post("/users/", json={
            "email": "newprovider@example.com",
            "password": "password123",
            "role": "PROVIDER",
            "profile": {
                "firstName": "New",
                "lastName": "Provider",
                "phone": "+1234567890",
                "address": "456 Provider St"
            }
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newprovider@example.com"
        assert data["role"] == "PROVIDER"
    
    def test_login_consumer(self, client, sample_consumer):
        """Test consumer login"""
        response = client.post("/auth/login", json={
            "email": "consumer123@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_provider(self, client, sample_provider):
        """Test provider login"""
        response = client.post("/auth/login", json={
            "email": "provider123@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_with_wrong_password(self, client, sample_consumer):
        """Test login fails with wrong password"""
        response = client.post("/auth/login", json={
            "email": "consumer123@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without authentication"""
        response = client.post("/services/", json={
            "name": "Test Service",
            "description": "Should fail",
            "price": 50.0,
            "durationMinutes": 60,
            "availability": {}
        })
        
        assert response.status_code == 401


class TestServiceManagementAPI:
    """Test service management API endpoints"""
    
    def test_provider_create_service(self, client, provider_token):
        """Test provider can create a service"""
        response = client.post(
            "/services/",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={
                "name": "New Service",
                "description": "Test service description",
                "price": 75.0,
                "durationMinutes": 60,
                "availability": {
                    "monday": ["09:00", "17:00"],
                    "friday": ["09:00", "17:00"]
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Service"
        assert data["price"] == 75.0
        assert "availability" in data
    
    def test_consumer_cannot_create_service(self, client, consumer_token):
        """Test consumer cannot create a service"""
        response = client.post(
            "/services/",
            headers={"Authorization": f"Bearer {consumer_token}"},
            json={
                "name": "Unauthorized Service",
                "description": "Should fail",
                "price": 50.0,
                "durationMinutes": 60,
                "availability": {}
            }
        )
        
        assert response.status_code == 403
    
    def test_anyone_can_browse_services(self, client, sample_service):
        """Test anyone can browse services without authentication"""
        response = client.get("/services/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_provider_update_own_service(self, client, provider_token, sample_service):
        """Test provider can update their own service"""
        response = client.put(
            f"/services/{sample_service.id}",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={
                "name": "Updated Service",
                "description": "Updated description",
                "price": 100.0,
                "durationMinutes": 90,
                "availability": {
                    "monday": ["10:00", "18:00"]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Service"
        assert data["price"] == 100.0
    
    def test_provider_cannot_update_others_service(self, client, other_provider_token, sample_service):
        """Test provider cannot update another provider's service"""
        response = client.put(
            f"/services/{sample_service.id}",
            headers={"Authorization": f"Bearer {other_provider_token}"},
            json={
                "name": "Hacked Service",
                "description": "Should fail",
                "price": 1.0,
                "durationMinutes": 1,
                "availability": {}
            }
        )
        
        assert response.status_code == 403
    
    def test_provider_delete_own_service(self, client, provider_token, sample_service):
        """Test provider can delete their own service"""
        response = client.delete(
            f"/services/{sample_service.id}",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        
        assert response.status_code == 204
    
    def test_consumer_cannot_delete_service(self, client, consumer_token, sample_service):
        """Test consumer cannot delete a service"""
        response = client.delete(
            f"/services/{sample_service.id}",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        assert response.status_code == 403


class TestBookingAPI:
    """Test booking API endpoints"""
    
    def test_consumer_create_booking_with_payment(self, client, consumer_token, sample_service):
        """Test consumer can book a service with payment"""
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
        
        booking_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post(
            "/bookings/",
            headers={"Authorization": f"Bearer {consumer_token}"},
            json={
                "serviceId": sample_service.id,
                "scheduledAt": booking_date,
                "notes": "Test booking",
                "payment": {
                    "bookingId": "temp",
                    "amount": sample_service.price,
                    "currency": "USD",
                    "paymentMethod": {
                        "type": "card",
                        "cardNumber": "4111111111111111",
                        "cardholderName": "Jane Consumer",
                        "expiryMonth": 12,
                        "expiryYear": 2025,
                        "cvv": "123"
                    }
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "CONFIRMED"
        assert data["totalAmount"] == sample_service.price
    
    def test_booking_fails_without_authentication(self, client, sample_service):
        """Test booking fails without authentication"""
        booking_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post(
            "/bookings/",
            json={
                "serviceId": sample_service.id,
                "scheduledAt": booking_date,
                "notes": "Should fail",
                "payment": {
                    "bookingId": "temp",
                    "amount": 100.0,
                    "currency": "USD",
                    "paymentMethod": {
                        "type": "card",
                        "cardNumber": "4111111111111111",
                        "cardholderName": "Jane Consumer",
                        "expiryMonth": 12,
                        "expiryYear": 2025,
                        "cvv": "123"
                    }
                }
            }
        )
        
        assert response.status_code == 401
    
    def test_booking_fails_for_nonexistent_service(self, client, consumer_token):
        """Test booking fails for non-existent service"""
        booking_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post(
            "/bookings/",
            headers={"Authorization": f"Bearer {consumer_token}"},
            json={
                "serviceId": "nonexistent-id",
                "scheduledAt": booking_date,
                "notes": "Should fail",
                "payment": {
                    "bookingId": "temp",
                    "amount": 100.0,
                    "currency": "USD",
                    "paymentMethod": {
                        "type": "card",
                        "cardNumber": "4111111111111111",
                        "cardholderName": "Jane Consumer",
                        "expiryMonth": 12,
                        "expiryYear": 2025,
                        "cvv": "123"
                    }
                }
            }
        )
        
        assert response.status_code == 404
    
    def test_consumer_view_own_bookings(self, client, consumer_token, sample_booking):
        """Test consumer can view their own bookings"""
        response = client.get(
            f"/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_booking.id
    
    def test_consumer_cannot_view_others_booking(self, client, other_consumer_token, sample_booking):
        """Test consumer cannot view another consumer's booking"""
        response = client.get(
            f"/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {other_consumer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_provider_can_view_their_service_booking(self, client, provider_token, sample_booking):
        """Test provider can view bookings for their services"""
        response = client.get(
            f"/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        
        assert response.status_code == 200
    
    def test_consumer_cancel_own_booking(self, client, consumer_token, sample_booking):
        """Test consumer can cancel their own booking"""
        response = client.delete(
            f"/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        assert response.status_code == 204
    
    def test_consumer_cannot_cancel_others_booking(self, client, other_consumer_token, sample_booking):
        """Test consumer cannot cancel another consumer's booking"""
        response = client.delete(
            f"/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {other_consumer_token}"}
        )
        
        assert response.status_code == 403


class TestCompleteUserFlow:
    """Test complete user journey flows"""
    
    def test_complete_consumer_journey(self, client):
        """Test complete consumer journey from registration to booking"""
        # 1. Register
        register_response = client.post("/users/", json={
            "email": "journey_consumer@example.com",
            "password": "password123",
            "role": "CUSTOMER",
            "profile": {
                "firstName": "Journey",
                "lastName": "Consumer",
                "phone": "+1234567890",
                "address": "123 Journey St"
            }
        })
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post("/auth/login", json={
            "email": "journey_consumer@example.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Browse services
        services_response = client.get("/services/")
        assert services_response.status_code == 200
        services = services_response.json()
        assert len(services) > 0
        
        # 4. Book a service
        import os
        os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
        
        service = services[0]
        booking_date = (datetime.now() + timedelta(days=7)).isoformat()
        booking_response = client.post(
            "/bookings/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "serviceId": service["id"],
                "scheduledAt": booking_date,
                "notes": "Complete journey test",
                "payment": {
                    "bookingId": "temp",
                    "amount": service["price"],
                    "currency": "USD",
                    "paymentMethod": {
                        "type": "card",
                        "cardNumber": "4111111111111111",
                        "cardholderName": "Journey Consumer",
                        "expiryMonth": 12,
                        "expiryYear": 2025,
                        "cvv": "123"
                    }
                }
            }
        )
        assert booking_response.status_code == 201
        booking = booking_response.json()
        assert booking["status"] == "CONFIRMED"
        
        # 5. View booking
        view_response = client.get(
            f"/bookings/{booking['id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert view_response.status_code == 200
    
    def test_complete_provider_journey(self, client):
        """Test complete provider journey from registration to service management"""
        # 1. Register
        register_response = client.post("/users/", json={
            "email": "journey_provider@example.com",
            "password": "password123",
            "role": "PROVIDER",
            "profile": {
                "firstName": "Journey",
                "lastName": "Provider",
                "phone": "+1234567890",
                "address": "456 Journey Ave"
            }
        })
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post("/auth/login", json={
            "email": "journey_provider@example.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Create service
        create_response = client.post(
            "/services/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Journey Service",
                "description": "Complete journey test service",
                "price": 150.0,
                "durationMinutes": 120,
                "availability": {
                    "monday": ["09:00", "17:00"],
                    "wednesday": ["09:00", "17:00"],
                    "friday": ["09:00", "17:00"]
                }
            }
        )
        assert create_response.status_code == 201
        service = create_response.json()
        
        # 4. Update service
        update_response = client.put(
            f"/services/{service['id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Updated Journey Service",
                "description": "Updated description",
                "price": 175.0,
                "durationMinutes": 150,
                "availability": {
                    "monday": ["10:00", "18:00"],
                    "wednesday": ["10:00", "18:00"],
                    "friday": ["10:00", "18:00"]
                }
            }
        )
        assert update_response.status_code == 200
        
        # 5. View own service
        view_response = client.get(f"/services/{service['id']}")
        assert view_response.status_code == 200
        
        # 6. Delete service
        delete_response = client.delete(
            f"/services/{service['id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 204

