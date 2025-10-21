# Service Marketplace API Documentation

## Overview
A FastAPI-based service marketplace API that allows users to register, create services, and make bookings.

## Base URL
```
http://localhost:8000
```

## Authentication
The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Health Check

#### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

### Authentication Endpoints

#### 2. User Registration
**POST** `/users/`

Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "customer",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "role": "customer",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345"
  },
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

#### 3. User Login
**POST** `/auth/login`

Login with email and password.

**Request Body:**
```
username: user@example.com
password: password123
```

**Response:** `200 OK`
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 4. Get Current User
**GET** `/auth/me`

Get current authenticated user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "role": "customer",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345"
  }
}
```

### Password Reset Endpoints

#### 5. Request Password Reset
**POST** `/password-reset/request`

Request a password reset email for a user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "If the email exists in our system, you will receive a password reset link.",
  "success": true
}
```

**Note:** Always returns success for security reasons (doesn't reveal if email exists).

#### 6. Confirm Password Reset
**POST** `/password-reset/confirm`

Reset password using a valid reset token.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password has been successfully reset",
  "success": true
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Invalid or expired reset token"
}
```

#### 7. Cleanup Expired Tokens
**POST** `/password-reset/cleanup`

Clean up expired password reset tokens (admin endpoint).

**Response:** `200 OK`
```json
{
  "message": "Cleaned up X expired tokens",
  "cleaned_count": 5
}
```

### User Management Endpoints

#### 8. List Users
**GET** `/users/`

List all users with optional role filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `role` (optional): Filter by role (`customer` or `provider`)

**Response:** `200 OK`
```json
[
  {
    "id": "user-uuid",
    "email": "user@example.com",
    "role": "customer",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+1234567890",
      "address": "123 Main St, City, State 12345"
    }
  }
]
```

#### 9. Get User by Email
**GET** `/users/{email}`

Get a specific user by email.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "role": "customer",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345"
  }
}
```

### Service Management Endpoints

#### 10. List Services
**GET** `/services/`

List all available services.

**Response:** `200 OK`
```json
[
  {
    "id": "service-uuid",
    "providerId": "provider-uuid",
    "title": "Web Development",
    "description": "Professional web development services",
    "category": "technology",
    "price": 100.0,
    "currency": "USD",
    "duration": 60,
    "availability": {
      "monday": [{"start": "09:00", "end": "17:00"}],
      "tuesday": [{"start": "09:00", "end": "17:00"}],
      "wednesday": [{"start": "09:00", "end": "17:00"}],
      "thursday": [{"start": "09:00", "end": "17:00"}],
      "friday": [{"start": "09:00", "end": "17:00"}],
      "saturday": [],
      "sunday": []
    },
    "images": ["image1.jpg", "image2.jpg"],
    "isActive": true,
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
```

#### 11. Get Service
**GET** `/services/{service_id}`

Get a specific service by ID.

**Response:** `200 OK`
```json
{
  "id": "service-uuid",
  "providerId": "provider-uuid",
  "title": "Web Development",
  "description": "Professional web development services",
  "category": "technology",
  "price": 100.0,
  "currency": "USD",
  "duration": 60,
  "availability": {
    "monday": [{"start": "09:00", "end": "17:00"}],
    "tuesday": [{"start": "09:00", "end": "17:00"}],
    "wednesday": [{"start": "09:00", "end": "17:00"}],
    "thursday": [{"start": "09:00", "end": "17:00"}],
    "friday": [{"start": "09:00", "end": "17:00"}],
    "saturday": [],
    "sunday": []
  },
  "images": ["image1.jpg", "image2.jpg"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 12. Create Service
**POST** `/services/`

Create a new service (provider only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "providerId": "provider-uuid",
  "title": "Web Development",
  "description": "Professional web development services",
  "category": "technology",
  "price": 100.0,
  "currency": "USD",
  "duration": 60,
  "availability": {
    "monday": [{"start": "09:00", "end": "17:00"}],
    "tuesday": [{"start": "09:00", "end": "17:00"}],
    "wednesday": [{"start": "09:00", "end": "17:00"}],
    "thursday": [{"start": "09:00", "end": "17:00"}],
    "friday": [{"start": "09:00", "end": "17:00"}],
    "saturday": [],
    "sunday": []
  },
  "images": ["image1.jpg", "image2.jpg"]
}
```

**Response:** `201 Created`
```json
{
  "id": "service-uuid",
  "providerId": "provider-uuid",
  "title": "Web Development",
  "description": "Professional web development services",
  "category": "technology",
  "price": 100.0,
  "currency": "USD",
  "duration": 60,
  "availability": {
    "monday": [{"start": "09:00", "end": "17:00"}],
    "tuesday": [{"start": "09:00", "end": "17:00"}],
    "wednesday": [{"start": "09:00", "end": "17:00"}],
    "thursday": [{"start": "09:00", "end": "17:00"}],
    "friday": [{"start": "09:00", "end": "17:00"}],
    "saturday": [],
    "sunday": []
  },
  "images": ["image1.jpg", "image2.jpg"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 13. Update Service
**PUT** `/services/{service_id}`

Update an existing service (provider only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated Web Development",
  "description": "Updated description",
  "price": 150.0
}
```

**Response:** `200 OK`
```json
{
  "id": "service-uuid",
  "providerId": "provider-uuid",
  "title": "Updated Web Development",
  "description": "Updated description",
  "category": "technology",
  "price": 150.0,
  "currency": "USD",
  "duration": 60,
  "availability": {
    "monday": [{"start": "09:00", "end": "17:00"}],
    "tuesday": [{"start": "09:00", "end": "17:00"}],
    "wednesday": [{"start": "09:00", "end": "17:00"}],
    "thursday": [{"start": "09:00", "end": "17:00"}],
    "friday": [{"start": "09:00", "end": "17:00"}],
    "saturday": [],
    "sunday": []
  },
  "images": ["image1.jpg", "image2.jpg"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 14. Delete Service
**DELETE** `/services/{service_id}`

Delete a service (provider only).

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Service deleted successfully"
}
```

### Booking Management Endpoints

#### 15. List Bookings
**GET** `/bookings/`

List bookings with optional filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `customerId` (optional): Filter by customer ID
- `providerId` (optional): Filter by provider ID

**Response:** `200 OK`
```json
[
  {
    "id": "booking-uuid",
    "customerId": "customer-uuid",
    "serviceId": "service-uuid",
    "providerId": "provider-uuid",
    "status": "pending",
    "scheduledAt": "2024-01-15T10:00:00Z",
    "duration": 60,
    "totalAmount": 100.0,
    "notes": "Please arrive on time",
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
```

#### 16. Get Booking
**GET** `/bookings/{booking_id}`

Get a specific booking by ID.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "booking-uuid",
  "customerId": "customer-uuid",
  "serviceId": "service-uuid",
  "providerId": "provider-uuid",
  "status": "pending",
  "scheduledAt": "2024-01-15T10:00:00Z",
  "duration": 60,
  "totalAmount": 100.0,
  "notes": "Please arrive on time",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 17. Create Booking
**POST** `/bookings/`

Create a new booking.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "serviceId": "service-uuid",
  "scheduledAt": "2024-01-15T10:00:00Z",
  "notes": "Please arrive on time"
}
```

**Response:** `201 Created`
```json
{
  "id": "booking-uuid",
  "customerId": "customer-uuid",
  "serviceId": "service-uuid",
  "providerId": "provider-uuid",
  "status": "pending",
  "scheduledAt": "2024-01-15T10:00:00Z",
  "duration": 60,
  "totalAmount": 100.0,
  "notes": "Please arrive on time",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 18. Update Booking
**PUT** `/bookings/{booking_id}`

Update an existing booking.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "confirmed",
  "scheduledAt": "2024-01-15T11:00:00Z",
  "notes": "Updated notes"
}
```

**Response:** `200 OK`
```json
{
  "id": "booking-uuid",
  "customerId": "customer-uuid",
  "serviceId": "service-uuid",
  "providerId": "provider-uuid",
  "status": "confirmed",
  "scheduledAt": "2024-01-15T11:00:00Z",
  "duration": 60,
  "totalAmount": 100.0,
  "notes": "Updated notes",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 19. Delete Booking
**DELETE** `/bookings/{booking_id}`

Delete a booking.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Booking deleted successfully"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Data Models

### User
```json
{
  "id": "string (UUID)",
  "email": "string (email)",
  "password": "string (hashed)",
  "role": "customer | provider",
  "profile": {
    "firstName": "string",
    "lastName": "string",
    "phone": "string",
    "address": "string"
  },
  "createdAt": "datetime (ISO 8601)",
  "updatedAt": "datetime (ISO 8601)"
}
```

### Service
```json
{
  "id": "string (UUID)",
  "providerId": "string (UUID)",
  "title": "string",
  "description": "string",
  "category": "string",
  "price": "number",
  "currency": "string (3 chars)",
  "duration": "number (minutes)",
  "availability": {
    "monday": [{"start": "string", "end": "string"}],
    "tuesday": [{"start": "string", "end": "string"}],
    "wednesday": [{"start": "string", "end": "string"}],
    "thursday": [{"start": "string", "end": "string"}],
    "friday": [{"start": "string", "end": "string"}],
    "saturday": [{"start": "string", "end": "string"}],
    "sunday": [{"start": "string", "end": "string"}]
  },
  "images": ["string"],
  "isActive": "boolean",
  "createdAt": "datetime (ISO 8601)"
}
```

### Booking
```json
{
  "id": "string (UUID)",
  "customerId": "string (UUID)",
  "serviceId": "string (UUID)",
  "providerId": "string (UUID)",
  "status": "pending | confirmed | completed | cancelled",
  "scheduledAt": "datetime (ISO 8601)",
  "duration": "number (minutes)",
  "totalAmount": "number",
  "notes": "string",
  "createdAt": "datetime (ISO 8601)"
}
```

## Rate Limiting
Currently no rate limiting is implemented. In production, consider implementing rate limiting for API endpoints.

## CORS
CORS is not configured. In production, configure CORS to allow specific origins.

## Security Notes
- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes by default
- Password reset tokens expire after 24 hours
- All database queries use parameterized statements to prevent SQL injection
- Input validation is performed on all endpoints
