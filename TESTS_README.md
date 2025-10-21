# Test Suite Documentation

## Overview
Comprehensive test suite for the Service Marketplace API with authentication and authorization checks.

## Test Structure

### Unit Tests (`tests/unit/`)

1. **test_authentication.py** - Authentication Tests
   - JWT token generation and validation
   - User login with correct/incorrect credentials
   - Token expiration handling
   - Tests for both consumer and provider roles

2. **test_authorization.py** - Authorization Tests
   - Service management authorization (providers only)
   - Ownership checks (providers can only modify their own services)
   - Booking authorization (consumers and providers)
   - Cross-user access prevention

3. **test_booking_flow.py** - Booking Flow Tests
   - Complete booking creation with payment processing
   - Authentication requirements for booking
   - Payment failure handling (10% failure rate)
   - Service validation (must exist)
   - Booking data integrity (duration, amount)

### Integration Tests (`tests/integration/`)

1. **test_api_complete.py** - Complete API Tests
   - **Authentication API**: Register, login, logout flows
   - **Service Management API**: CRUD operations with role checks
   - **Booking API**: Complete booking lifecycle
   - **Complete User Journeys**: End-to-end consumer and provider flows

## Test Scenarios Covered

### Authentication & Authorization
- ✅ Consumer can register and login
- ✅ Provider can register and login  
- ✅ Login fails with wrong password
- ✅ Login fails for non-existent users
- ✅ Protected routes require authentication
- ✅ JWT tokens contain correct user information

### Service Management
- ✅ Provider can create services with availability
- ✅ Provider can update their own services
- ✅ Provider can delete their own services
- ✅ Provider CANNOT update other providers' services
- ✅ Provider CANNOT delete other providers' services
- ✅ Consumer CANNOT create services (403 Forbidden)
- ✅ Consumer CANNOT delete services (403 Forbidden)
- ✅ Anyone can browse services without authentication

### Booking System
- ✅ Consumer can book services with payment
- ✅ Booking requires authentication (401 without token)
- ✅ Booking requires valid service (404 for non-existent)
- ✅ Booking fails if payment fails
- ✅ Booking stores correct duration and amount
- ✅ Consumer can view their own bookings
- ✅ Consumer CANNOT view other consumers' bookings
- ✅ Provider can view bookings for their services
- ✅ Consumer can cancel their own bookings
- ✅ Provider can cancel bookings for their services
- ✅ Users CANNOT cancel other users' bookings

### Payment Processing
- ✅ Payment record is created for each booking
- ✅ Payment can fail (configurable 10% rate)
- ✅ Failed payments trigger refunds
- ✅ Bookings are not created if payment fails

## Running Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run in Quick Mode
```bash
python run_all_tests.py --quick
```

### Run with Coverage Report
```bash
python run_all_tests.py --coverage
```

### Run Specific Test File
```bash
source venv/bin/activate
pytest tests/unit/test_authentication.py -v
```

### Run Specific Test
```bash
source venv/bin/activate
pytest tests/unit/test_authentication.py::TestAuthentication::test_successful_authentication_consumer -v
```

## Test Configuration

Tests use a separate test database to avoid affecting production data:
- **Test Database**: `marketplace_test`
- **Payment Failure Rate**: Set to 0% during tests for consistency
- **Test Isolation**: Each test gets a fresh database schema

## Test Fixtures

### Database Fixtures
- `test_db` - Clean test database session for each test
- `client` - TestClient for API testing

### User Fixtures
- `sample_consumer` - Pre-created consumer user
- `sample_provider` - Pre-created provider user
- `other_consumer` - Additional consumer for authorization tests
- `other_provider` - Additional provider for authorization tests

### Authentication Fixtures
- `consumer_token` - JWT token for consumer
- `provider_token` - JWT token for provider
- `other_consumer_token` - JWT token for other consumer
- `other_provider_token` - JWT token for other provider

### Data Fixtures
- `sample_service` - Pre-created service with availability
- `sample_booking` - Pre-created confirmed booking

## Key Test Patterns

### Authorization Testing Pattern
```python
def test_provider_cannot_update_others_service(
    self, client, other_provider_token, sample_service
):
    """Test provider cannot update another provider's service"""
    response = client.put(
        f"/services/{sample_service.id}",
        headers={"Authorization": f"Bearer {other_provider_token}"},
        json={...}
    )
    assert response.status_code == 403
```

### Complete Flow Testing Pattern
```python
def test_complete_consumer_journey(self, client):
    """Test complete consumer journey"""
    # 1. Register
    # 2. Login
    # 3. Browse services
    # 4. Book service with payment
    # 5. View booking
    assert all_steps_successful
```

## Continuous Testing

The test suite is designed to be run:
- Before committing code
- In CI/CD pipelines
- After any authentication/authorization changes
- After database schema changes

## Future Enhancements

Potential additions to the test suite:
- Rate limiting tests
- SSE notification tests
- Password reset flow tests
- Email notification content validation
- Performance/load testing
- Security penetration testing

