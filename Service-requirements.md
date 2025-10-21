# Backend Developer Test: Service Marketplace API

## Overview
You have **2 days** to build a complete backend API for a service marketplace where users can book various services. This is a full-stack backend test that should demonstrate your skills in API design, database modeling, authentication, testing, and deployment.

## Requirements

### Core Features
1. **User Management**
   - User registration and authentication (JWT)
   - User profiles (customer and service provider roles)
   - Password reset functionality

2. **Service Management**
   - Service providers can create, update, and delete services
   - Services have categories, descriptions, pricing, availability
   - Service search and filtering capabilities

3. **Booking System**
   - Customers can book services for specific time slots
   - Booking status management (pending, confirmed, completed, cancelled)
   - Booking history and management

4. **Payment Integration**
   - Mock payment processing (no real payment gateway needed)
   - Payment status tracking
   - Refund handling

5. **Notification System**
   - Email notifications for booking confirmations, updates -- we can mock this for now (File based mock?)
   - Real-time notifications (WebSocket or Server-Sent Events)

### Technical Requirements

#### Backend Stack
- **Language**: Python (Django/FastAPI) or Node.js (Express/NestJS) or Java (Spring Boot)
- **Database**: PostgreSQL or MongoDB
- **Authentication**: JWT tokens
- **API**: RESTful API with proper HTTP status codes
- **Documentation**: OpenAPI/Swagger documentation

#### Database Design
- Design a normalized database schema
- Include proper relationships and constraints
- Consider indexing for performance

#### API Endpoints
Create comprehensive REST API endpoints for:
- Authentication (`/auth/*`)
- User management (`/users/*`)
- Services (`/services/*`)
- Bookings (`/bookings/*`)
- Payments (`/payments/*`)
- Notifications (`/notifications/*`)

#### Testing
- **Unit tests**: Minimum 80% code coverage
- **Integration tests**: Test API endpoints
- **Test data**: Seed data for development and testing

#### Additional Features
- **Rate limiting**: Implement API rate limiting
- **Logging**: Structured logging with different levels
- **Error handling**: Comprehensive error handling and validation
- **Caching**: Implement caching where appropriate
- **File uploads**: Handle service images/documentation
- **Search**: Implement search functionality with filters

## Deliverables

### 1. Code Repository
- Well-structured, clean code following best practices
- Proper project structure and organization
- Environment configuration files
- Database migrations/seeders

### 2. Documentation
- **API Documentation**: Complete OpenAPI/Swagger documentation
- **Setup Instructions**: Clear instructions to run the project
- **Database Schema**: ERD or schema documentation
- **Architecture Overview**: Brief explanation of your design decisions

### 3. Testing
- Test suite with good coverage
- Test data and fixtures
- Instructions on how to run tests

### 4. Deployment
- Docker configuration (Dockerfile + docker-compose.yml)
- Environment variables configuration
- Basic deployment instructions

## Evaluation Criteria

### Technical Skills (40%)
- Code quality and architecture
- Database design and optimization
- API design and RESTful principles
- Error handling and validation

### Testing (25%)
- Test coverage and quality
- Test organization and maintainability
- Integration testing approach

### Documentation (15%)
- API documentation completeness
- Code documentation and comments
- Setup and deployment instructions

### Additional Features (20%)
- Implementation of bonus features
- Performance considerations
- Security best practices
- Code organization and maintainability

## Bonus Points
- Implement real-time features (WebSockets/SSE)
- Add comprehensive logging and monitoring
- Implement caching strategies
- Add data validation and sanitization
- Include performance optimization
- Add comprehensive error handling
- Implement proper security measures
- Add API versioning
- Include database query optimization

## Sample Data Models

### User
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "password": "hashed_password",
  "role": "customer|provider",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St"
  },
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Service
```json
{
  "id": "uuid",
  "providerId": "uuid",
  "title": "House Cleaning",
  "description": "Professional house cleaning service",
  "category": "home_services",
  "price": 50.00,
  "currency": "USD",
  "duration": 120,
  "availability": {
    "monday": ["09:00", "17:00"],
    "tuesday": ["09:00", "17:00"]
  },
  "images": ["url1", "url2"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### Booking
```json
{
  "id": "uuid",
  "customerId": "uuid",
  "serviceId": "uuid",
  "providerId": "uuid",
  "status": "pending|confirmed|completed|cancelled",
  "scheduledAt": "2024-01-15T10:00:00Z",
  "duration": 120,
  "totalAmount": 50.00,
  "notes": "Please clean the kitchen thoroughly",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

## Submission

Please submit your solution as a pull request with:
- Complete source code
- Comprehensive README with setup instructions
- Test results and coverage report
- API documentation
- Any additional notes about your implementation

## Questions?

If you have any questions about the requirements, please reach out. Good luck!

---

**Time Limit**: 2 days from the start of this test
**Deadline**: [Specify the exact deadline]