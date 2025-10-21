# Service Marketplace API - Backend Developer Test Submission

## Overview
This is a complete backend API implementation for a service marketplace where users can book various services. The system supports two user roles: **Customers** (who book services) and **Service Providers** (who offer services).

Built with **FastAPI**, **PostgreSQL**, **Redis**, and containerized with **Docker** for one-click deployment.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Features](#core-features)
3. [Technical Stack](#technical-stack)
4. [API Documentation](#api-documentation)
5. [Testing Instructions](#testing-instructions)
6. [Database Schema](#database-schema)
7. [Architecture Overview](#architecture-overview)
8. [Security Features](#security-features)
9. [Environment Configuration](#environment-configuration)

---

## Quick Start

### Option 1: Docker (Recommended - One Command!)

```bash
# Clone the repository
cd interview-test

# Start the entire application stack
docker-compose up

# The API will be available at:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - Alternative Docs: http://localhost:8000/redoc
```

That's it! The Docker setup automatically:
- ✅ Initializes PostgreSQL database
- ✅ Runs all migrations
- ✅ Seeds sample data
- ✅ Starts Redis for rate limiting
- ✅ Launches the FastAPI application

### Option 2: Local Development

```bash
# 1. Install dependencies
./setup.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Configure environment
cp env.template .env
# Edit .env with your database credentials

# 4. Initialize database
python init_db.py

# 5. Run migrations
python migrate.py

# 6. Start the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

---

## Core Features

### 1. User Management ✅

**Features Implemented:**
- User registration with email validation
- JWT-based authentication
- Role-based access control (Customer vs Service Provider)
- User profiles with comprehensive information
- Password reset functionality with secure tokens

**How to Test:**

#### Register a New Customer
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "SecurePass123!",
    "role": "CUSTOMER",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+1234567890",
      "address": "123 Main St, City, State"
    }
  }'
```

#### Register a Service Provider
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "provider@example.com",
    "password": "SecurePass123!",
    "role": "PROVIDER",
    "profile": {
      "firstName": "Jane",
      "lastName": "Smith",
      "phone": "+0987654321",
      "address": "456 Business Ave, City, State"
    }
  }'
```

#### Login and Get JWT Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=customer@example.com&password=SecurePass123!"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get User Profile
```bash
# Use the token from login
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Request Password Reset
```bash
curl -X POST http://localhost:8000/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com"
  }'
```

Check `email_notifications/` directory for the reset link.

#### Confirm Password Reset
```bash
curl -X POST http://localhost:8000/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL",
    "newPassword": "NewSecurePass123!"
  }'
```

---

### 2. Service Management ✅

**Features Implemented:**
- Service providers can create, update, and delete services
- Services include categories, descriptions, pricing, duration, availability schedules
- Service search and filtering
- Authorization checks (only service owners can modify their services)
- Service status management (ACTIVE, INACTIVE, SUSPENDED)

**How to Test:**

#### Create a Service (Provider Only)
```bash
# First, login as a provider and get the token
curl -X POST http://localhost:8000/services/ \
  -H "Authorization: Bearer PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Professional House Cleaning",
    "description": "Deep cleaning service for your entire home",
    "category": "home_services",
    "price": 75.00,
    "currency": "USD",
    "durationMinutes": 120,
    "availability": {
      "monday": ["09:00-12:00", "14:00-17:00"],
      "tuesday": ["09:00-12:00", "14:00-17:00"],
      "wednesday": ["09:00-12:00"],
      "friday": ["09:00-17:00"]
    },
    "images": ["https://example.com/cleaning1.jpg"],
    "isActive": true
  }'
```

#### Browse All Services (No Authentication Required)
```bash
curl -X GET http://localhost:8000/services/
```

#### Get Service Details
```bash
curl -X GET http://localhost:8000/services/{service_id}
```

#### Update Service (Owner Only)
```bash
curl -X PUT http://localhost:8000/services/{service_id} \
  -H "Authorization: Bearer PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Premium House Cleaning",
    "price": 85.00
  }'
```

#### Delete Service (Owner Only)
```bash
curl -X DELETE http://localhost:8000/services/{service_id} \
  -H "Authorization: Bearer PROVIDER_TOKEN"
```

#### Test Authorization
Try updating a service with a different provider's token or customer token - should get 403 Forbidden.

---

### 3. Booking System ✅

**Features Implemented:**
- Customers can book services for specific time slots
- Booking status management (PENDING, CONFIRMED, COMPLETED, CANCELLED)
- Booking history for customers and providers
- Authorization (customers can manage their bookings, providers can view bookings for their services)
- Automatic payment processing before booking confirmation

**How to Test:**

#### Create a Booking (Customer Only, with Payment)
```bash
curl -X POST http://localhost:8000/bookings/ \
  -H "Authorization: Bearer CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceId": "SERVICE_UUID_HERE",
    "scheduledAt": "2025-10-25T14:00:00Z",
    "notes": "Please bring eco-friendly cleaning supplies",
    "payment": {
      "amount": 75.00,
      "currency": "USD",
      "paymentMethod": {
        "type": "card",
        "last4": "4242",
        "brand": "visa"
      }
    }
  }'
```

**Expected Response (if payment succeeds):**
```json
{
  "id": "booking-uuid",
  "customerId": "customer-uuid",
  "serviceId": "service-uuid",
  "providerId": "provider-uuid",
  "status": "CONFIRMED",
  "scheduledAt": "2025-10-25T14:00:00Z",
  "duration": 120,
  "totalAmount": 75.00,
  "notes": "Please bring eco-friendly cleaning supplies",
  "createdAt": "2025-10-21T...",
  "updatedAt": "2025-10-21T..."
}
```

**Note:** Payment has a 10% failure rate (configurable). If payment fails, booking is not created and you'll receive an error.

#### View Customer's Bookings
```bash
curl -X GET http://localhost:8000/bookings/ \
  -H "Authorization: Bearer CUSTOMER_TOKEN"
```

#### View Provider's Bookings
```bash
curl -X GET http://localhost:8000/bookings/ \
  -H "Authorization: Bearer PROVIDER_TOKEN"
```

#### Get Specific Booking
```bash
curl -X GET http://localhost:8000/bookings/{booking_id} \
  -H "Authorization: Bearer CUSTOMER_OR_PROVIDER_TOKEN"
```

#### Update Booking Status (Provider)
```bash
curl -X PUT http://localhost:8000/bookings/{booking_id} \
  -H "Authorization: Bearer PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "COMPLETED"
  }'
```

#### Cancel Booking (Customer or Provider)
```bash
curl -X DELETE http://localhost:8000/bookings/{booking_id} \
  -H "Authorization: Bearer CUSTOMER_OR_PROVIDER_TOKEN"
```

#### Test Without Authentication
Try creating a booking without a token - should get 401 Unauthorized.

---

### 4. Payment Integration ✅

**Features Implemented:**
- Mock payment processing with realistic behavior
- 10% random failure rate (configurable via `PAYMENT_FAILURE_RATE` env variable)
- Payment status tracking (SUCCESS, FAILED, REFUNDED)
- Automatic refund on payment failure
- Transaction ID generation
- Payment history

**How to Test:**

#### Payment is Integrated with Booking
Payment happens automatically when creating a booking (see Booking System above).

#### View Payment History
```bash
curl -X GET http://localhost:8000/payments/ \
  -H "Authorization: Bearer CUSTOMER_TOKEN"
```

#### Get Payment Details
```bash
curl -X GET http://localhost:8000/payments/{payment_id} \
  -H "Authorization: Bearer CUSTOMER_TOKEN"
```

#### Process Refund (Provider Only)
```bash
curl -X POST http://localhost:8000/payments/{payment_id}/refund \
  -H "Authorization: Bearer PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Service cancelled by provider"
  }'
```

#### Test Payment Failure
Set `PAYMENT_FAILURE_RATE=1.0` in `.env` to force all payments to fail, then try creating a booking. The booking should not be created, and you should receive a payment failure error.

Reset to `PAYMENT_FAILURE_RATE=0.1` for normal operation.

---

### 5. Notification System ✅

**Features Implemented:**
- Email notifications for booking events (file-based mock)
- Real-time notifications via Server-Sent Events (SSE)
- Notification types: booking_created, booking_cancelled, booking_completed, payment_received, payment_failed
- User-specific notification targeting
- Read/unread status tracking

**How to Test:**

#### Email Notifications (File-Based Mock)
Email notifications are automatically sent for:
- Booking confirmation (to customer and provider)
- Booking cancellation
- Booking updates
- Payment confirmations

**Check emails:**
```bash
ls -la email_notifications/
cat email_notifications/booking_confirmation_*.txt
cat email_notifications/booking_notification_provider_*.txt
```

#### Real-Time Notifications (SSE)
Open SSE connection to receive real-time notifications:

```bash
# In a terminal, keep this connection open
curl -N -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/notifications/stream
```

In another terminal, perform actions (create booking, cancel booking, etc.) and watch notifications appear in real-time!

#### Get Notification History
```bash
curl -X GET http://localhost:8000/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Mark Notification as Read
```bash
curl -X PUT http://localhost:8000/notifications/{notification_id}/read \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Unread Count
```bash
curl -X GET http://localhost:8000/notifications/unread/count \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Technical Stack

### Backend Framework
- **FastAPI 0.104.1** - Modern, fast web framework for building APIs
- **Uvicorn 0.24.0** - ASGI server
- **Python 3.11+** - Programming language

### Database
- **PostgreSQL 15** - Primary database
- **SQLAlchemy 2.0.36** - SQL toolkit and ORM
- **Psycopg 3.1.18** - PostgreSQL adapter
- **Alembic 1.13.1** - Database migrations

### Authentication & Security
- **Python-JOSE 3.3.0** - JWT token handling
- **Passlib + Bcrypt 4.1.2** - Password hashing
- **Python-Multipart 0.0.6** - Form data handling

### Caching & Rate Limiting
- **Redis 6.4.0** - In-memory data store
- **SlowAPI 0.1.9** - Rate limiting middleware

### Testing
- **Pytest 7.4.3** - Testing framework
- **Pytest-asyncio 0.21.1** - Async test support
- **Pytest-cov 4.1.0** - Coverage reporting
- **HTTPX 0.25.2** - HTTP client for API testing

### Logging
- **Structlog 25.4.0** - Structured logging

### Data Validation
- **Pydantic 2.12.3** - Data validation and serialization
- **Email-validator 2.1.0** - Email validation

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

---

## API Documentation

### Interactive Documentation

Once the application is running, access comprehensive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API explorer
  - Try out endpoints directly in the browser
  - See request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation format
  - Clean, easy-to-read interface

### API Endpoints Summary

#### Authentication (`/auth/*`)
- `POST /auth/login` - User login, get JWT token
- `POST /auth/logout` - User logout

#### Users (`/users/*`)
- `POST /users/` - Register new user
- `GET /users/me` - Get current user profile
- `PUT /users/{user_id}` - Update user profile
- `DELETE /users/{user_id}` - Delete user account
- `GET /users/{user_id}` - Get user by ID (admin)

#### Services (`/services/*`)
- `POST /services/` - Create service (provider only)
- `GET /services/` - List all services
- `GET /services/{service_id}` - Get service details
- `PUT /services/{service_id}` - Update service (owner only)
- `DELETE /services/{service_id}` - Delete service (owner only)

#### Bookings (`/bookings/*`)
- `POST /bookings/` - Create booking with payment (customer only)
- `GET /bookings/` - List user's bookings
- `GET /bookings/{booking_id}` - Get booking details
- `PUT /bookings/{booking_id}` - Update booking status
- `DELETE /bookings/{booking_id}` - Cancel booking

#### Payments (`/payments/*`)
- `GET /payments/` - List user's payments
- `GET /payments/{payment_id}` - Get payment details
- `POST /payments/{payment_id}/refund` - Process refund

#### Notifications (`/notifications/*`)
- `GET /notifications/` - List notifications
- `GET /notifications/stream` - SSE stream for real-time notifications
- `PUT /notifications/{notification_id}/read` - Mark as read
- `GET /notifications/unread/count` - Get unread count

#### Password Reset (`/password-reset/*`)
- `POST /password-reset/request` - Request password reset
- `POST /password-reset/confirm` - Confirm password reset with token

---

## Testing Instructions

### Run All Tests

#### Option 1: Docker Tests (Recommended)
```bash
# Run complete test suite in isolated Docker environment
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# View test results
# Tests will run automatically and display results
```

#### Option 2: Local Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with coverage
python run_all_tests.py

# Or run specific test categories
pytest tests/unit/test_authentication.py -v
pytest tests/unit/test_authorization.py -v
pytest tests/unit/test_booking_flow.py -v
pytest tests/integration/test_api_complete.py -v
```

### Test Coverage

The test suite includes:
- **Unit Tests**: 15 tests covering authentication, authorization, and booking logic
- **Integration Tests**: 23 tests covering complete API workflows

**Test Categories:**
1. **Authentication Tests** - JWT token generation, login, logout
2. **Authorization Tests** - Role-based access control, ownership checks
3. **Booking Flow Tests** - Complete booking lifecycle with payment
4. **API Integration Tests** - End-to-end user journeys

### Manual Testing Scenarios

#### Scenario 1: Complete Customer Journey
```bash
# 1. Register as customer
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test.customer@example.com","password":"Test123!","role":"CUSTOMER","profile":{"firstName":"Test","lastName":"Customer","phone":"+1111111111","address":"Test Address"}}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=test.customer@example.com&password=Test123!"
# Save the access_token

# 3. Browse services
curl -X GET http://localhost:8000/services/

# 4. Book a service (use service_id from step 3)
curl -X POST http://localhost:8000/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceId":"SERVICE_ID","scheduledAt":"2025-10-30T10:00:00Z","notes":"Test booking","payment":{"amount":50.00,"currency":"USD","paymentMethod":{"type":"card","last4":"4242","brand":"visa"}}}'

# 5. View bookings
curl -X GET http://localhost:8000/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Check notifications
curl -X GET http://localhost:8000/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Scenario 2: Complete Provider Journey
```bash
# 1. Register as provider
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test.provider@example.com","password":"Test123!","role":"PROVIDER","profile":{"firstName":"Test","lastName":"Provider","phone":"+2222222222","address":"Provider Address"}}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=test.provider@example.com&password=Test123!"

# 3. Create a service
curl -X POST http://localhost:8000/services/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Service","description":"Test Description","category":"test","price":50.00,"currency":"USD","durationMinutes":60,"availability":{"monday":["09:00-17:00"]},"images":[],"isActive":true}'

# 4. View bookings for your services
curl -X GET http://localhost:8000/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Update booking status
curl -X PUT http://localhost:8000/bookings/{booking_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"COMPLETED"}'
```

#### Scenario 3: Authorization Tests
```bash
# Test 1: Customer tries to create service (should fail with 403)
curl -X POST http://localhost:8000/services/ \
  -H "Authorization: Bearer CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...service data...}'

# Test 2: Provider tries to update another provider's service (should fail with 403)
curl -X PUT http://localhost:8000/services/{other_provider_service_id} \
  -H "Authorization: Bearer PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...update data...}'

# Test 3: Unauthenticated user tries to book (should fail with 401)
curl -X POST http://localhost:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{...booking data...}'
```

#### Scenario 4: Rate Limiting Tests
```bash
# Try to login 6 times in rapid succession (limit is 5/hour)
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -d "username=test@example.com&password=wrong"
  echo "Attempt $i"
done
# The 6th attempt should return 429 Too Many Requests
```

---

## Database Schema

### Entity Relationship Overview

```
Users (1) ----< (M) Services
  |                    |
  |                    |
  +--> (M) Bookings <--+
         |
         |
         +--> (1) Payments
         |
         +--> (M) Notifications
         
Users (1) ----< (M) PasswordResetTokens
```

### Tables

#### 1. users
- **Primary Key**: `id` (UUID)
- **Unique**: `email`
- **Fields**: email, password (hashed), role (CUSTOMER/PROVIDER), profile (JSONB), timestamps
- **Indexes**: email

#### 2. services
- **Primary Key**: `id` (UUID)
- **Foreign Key**: `provider_id` → users.id
- **Fields**: title, description, category, price, currency, duration_minutes, availability (JSONB), images (ARRAY), status, timestamps
- **Indexes**: provider_id, category, status

#### 3. bookings
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: 
  - `customer_id` → users.id
  - `service_id` → services.id
  - `provider_id` → users.id
- **Fields**: status (PENDING/CONFIRMED/COMPLETED/CANCELLED), scheduled_at, duration_minutes, total_amount, notes, timestamps
- **Indexes**: customer_id, service_id, provider_id, status

#### 4. payments
- **Primary Key**: `id` (UUID)
- **Foreign Key**: `booking_id` → bookings.id
- **Fields**: status (SUCCESS/FAILED/REFUNDED), transaction_id, amount, currency, payment_method (JSONB), failure_reason, timestamps
- **Indexes**: booking_id, status

#### 5. notifications
- **Primary Key**: `id` (UUID)
- **Fields**: user_id, type, title, message, data (JSONB), is_read, read_at, created_at
- **Indexes**: user_id, is_read

#### 6. password_reset_tokens
- **Primary Key**: `id` (UUID)
- **Fields**: email, token (unique), expires_at, used, created_at
- **Indexes**: token, email

### View Database Schema
```bash
# Connect to database
docker exec -it marketplace_db psql -U postgres -d service_marketplace

# List tables
\dt

# Describe table structure
\d users
\d services
\d bookings
\d payments
\d notifications

# View sample data
SELECT * FROM users;
SELECT * FROM services;
```

---

## Architecture Overview

### Design Pattern: MVC (Model-View-Controller)

```
┌─────────────────┐
│   Controllers   │  ← FastAPI route handlers (HTTP layer)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    Services     │  ← Business logic layer
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Repositories   │  ← Database access layer (SQLAlchemy)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   PostgreSQL    │  ← Data persistence
└─────────────────┘
```

### Directory Structure

```
interview-test/
├── controllers/          # API endpoints (route handlers)
│   ├── auth_controller.py
│   ├── users_controller.py
│   ├── services_controller.py
│   ├── bookings_controller.py
│   ├── payments_controller.py
│   ├── notifications_controller.py
│   └── password_reset_controller.py
│
├── services/            # Business logic
│   ├── users_service.py
│   ├── services_service.py
│   ├── bookings_service.py
│   ├── payments_service.py
│   ├── notifications_service.py
│   ├── email_service.py
│   ├── password_reset_service.py
│   └── sse_manager.py
│
├── repositories/        # Database operations
│   ├── users_repository.py
│   ├── services_repository.py
│   ├── bookings_repository.py
│   ├── payments_repository.py
│   ├── notifications_repository.py
│   └── password_reset_repository.py
│
├── models.py           # Pydantic models (request/response)
├── database.py         # SQLAlchemy configuration
├── auth.py             # JWT authentication utilities
├── rate_limiter.py     # Rate limiting configuration
├── logging_config.py   # Structured logging setup
│
├── tests/              # Test suite
│   ├── unit/
│   └── integration/
│
├── migrations/         # Database migrations
├── main.py            # Application entry point
├── init_db.py         # Database initialization
├── migrate.py         # Migration runner
│
├── docker-compose.yml      # Production Docker setup
├── docker-compose.test.yml # Test Docker setup
├── Dockerfile              # Application container
└── requirements.txt        # Python dependencies
```

### Key Design Decisions

1. **MVC Architecture**: Clear separation of concerns for maintainability
2. **Repository Pattern**: Abstracts database operations for easy testing
3. **Dependency Injection**: FastAPI's DI system for loose coupling
4. **Async/Await**: Asynchronous operations for better performance
5. **Pydantic Models**: Strong typing and validation
6. **JWT Authentication**: Stateless, scalable authentication
7. **Role-Based Access Control**: Flexible authorization system
8. **Mock Services**: File-based email for easy testing

---

## Security Features

### Authentication
- ✅ **JWT Tokens**: Secure, stateless authentication
- ✅ **Token Expiration**: 30-minute access token lifetime (configurable)
- ✅ **Password Hashing**: Bcrypt with salt for secure password storage
- ✅ **Password Reset**: Secure token-based reset with expiration

### Authorization
- ✅ **Role-Based Access Control (RBAC)**: Customer vs Provider roles
- ✅ **Ownership Checks**: Users can only modify their own resources
- ✅ **Protected Endpoints**: Authentication required for sensitive operations
- ✅ **Granular Permissions**: Different access levels per endpoint

### Data Protection
- ✅ **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- ✅ **Input Validation**: Pydantic models validate all inputs
- ✅ **Email Validation**: Proper email format checking
- ✅ **Password Strength**: Minimum requirements enforced
- ✅ **Environment Variables**: Sensitive data not in code

### Rate Limiting
- ✅ **Login Attempts**: 5 per hour per IP
- ✅ **Booking Creation**: 20 per hour per user
- ✅ **Service Browsing**: 100 per hour per IP
- ✅ **Configurable**: Adjust limits via environment variables

### Additional Security Measures
- ✅ **CORS Configuration**: Configured for production
- ✅ **Error Messages**: Generic errors, no sensitive data leakage
- ✅ **Logging**: Security events logged for audit
- ✅ **Database Constraints**: Foreign keys, unique constraints enforced

---

## Environment Configuration

### Environment Variables

Copy `env.template` to `.env` and configure:

```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/service_marketplace
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/marketplace_test

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SECRET_KEY=your-secret-key-for-sessions

# Redis Configuration (for rate limiting)
REDIS_URL=redis://localhost:6379/0

# Payment Configuration
PAYMENT_FAILURE_RATE=0.1  # 10% failure rate for testing

# Rate Limiting Configuration
RATE_LIMIT_ENABLED=true
LOGIN_RATE_LIMIT=5/hour
BOOKING_RATE_LIMIT=20/hour
BROWSE_RATE_LIMIT=100/hour

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Environment

For Docker deployment, environment variables are configured in `docker-compose.yml`. The setup automatically handles:
- Database initialization
- Redis connection
- Application startup
- Migration execution

---

## Additional Features

### Implemented Bonus Features

✅ **Real-time Notifications** - Server-Sent Events (SSE) for live updates
✅ **Comprehensive Logging** - Structured logs with multiple outputs
✅ **Caching** - Redis integration for rate limiting and future caching
✅ **Rate Limiting** - Per-user and per-IP limits
✅ **Data Validation** - Extensive Pydantic validation
✅ **Error Handling** - Comprehensive error handling throughout
✅ **Security Measures** - Multiple layers of security
✅ **Performance Optimization** - Database indexes, async operations

### Performance Optimizations

- **Database Indexes**: On frequently queried fields
- **Connection Pooling**: SQLAlchemy connection pool
- **Async Operations**: Non-blocking I/O operations
- **Redis Caching**: Fast in-memory data access
- **Efficient Queries**: Optimized SQL queries

---

## Troubleshooting

### Common Issues

**Issue**: Database connection failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs marketplace_db

# Verify DATABASE_URL in .env
```

**Issue**: Redis connection failed
```bash
# Check if Redis is running
docker ps | grep redis

# Check Redis logs
docker logs marketplace_redis
```

**Issue**: Tests failing
```bash
# Ensure test database exists
docker exec marketplace_test_db psql -U postgres -c "CREATE DATABASE marketplace_test;"

# Run tests with verbose output
pytest tests/ -v -s
```

**Issue**: Rate limiting not working
```bash
# Verify Redis is running and REDIS_URL is correct
# Check rate_limiter.py configuration
# Ensure RATE_LIMIT_ENABLED=true in .env
```

---

## Development Workflow

### Running Locally with Hot Reload

```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision -m "description"

# Run migrations
python migrate.py

# Or use the provided migration system
# Edit migrations/XXX_name.py
# Run: python migrate.py
```

### Viewing Logs

```bash
# Application logs
tail -f logs/app.log

# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log

# Security logs
tail -f logs/security.log

# Database logs
tail -f logs/database.log
```

### Debugging

```bash
# Set log level to DEBUG in .env
LOG_LEVEL=DEBUG

# Run with Python debugger
python -m pdb main.py

# Or use VS Code/PyCharm debugger
```

---

## Support & Contact

For questions or issues:
1. Check the interactive API documentation at `/docs`
2. Review the test suite for usage examples
3. Check logs in the `logs/` directory
4. Review environment configuration in `.env`

---

## License

This is a test project for evaluation purposes.

