# Service Marketplace API

A FastAPI-based backend service for a service marketplace where users can book various services.

## Features

- **User Management**: Registration, authentication, and profile management
- **Service Management**: Create, update, and manage services
- **Booking System**: Book services with status management
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL Integration**: Persistent data storage
- **RESTful API**: Clean and well-documented endpoints

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **Pydantic** - Data validation

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd interview-test
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL**
```bash
# Install PostgreSQL (if not already installed)
brew install postgresql@14  # macOS
# or
sudo apt-get install postgresql  # Ubuntu

# Start PostgreSQL
brew services start postgresql@14  # macOS
# or
sudo systemctl start postgresql  # Ubuntu

# Create database
createdb service_marketplace
```

5. **Initialize database**
```bash
python init_db.py
```

6. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Project Structure

```
interview-test/
├── controllers/          # API route handlers
│   ├── auth_controller.py
│   ├── bookings_controller.py
│   ├── services_controller.py
│   └── users_controller.py
├── services/             # Business logic
│   ├── bookings_service.py
│   └── users_service.py
├── repositories/         # Data access layer
│   └── users_repository.py
├── models.py            # Pydantic models
├── auth.py              # Authentication utilities
├── database.py          # Database configuration
├── init_db.py           # Database initialization
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── API_DOCUMENTATION.md # API documentation
```

## Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123",
    "role": "customer",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+1234567890",
      "address": "123 Main St"
    }
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 3. Create a Service
```bash
curl -X POST "http://localhost:8000/services/?providerId=user-uuid" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "House Cleaning",
    "description": "Professional house cleaning service",
    "category": "home_services",
    "price": 50.0,
    "currency": "USD",
    "duration": 120,
    "availability": {
      "monday": ["09:00", "17:00"],
      "tuesday": ["09:00", "17:00"]
    },
    "images": []
  }'
```

### 4. Create a Booking
```bash
curl -X POST "http://localhost:8000/bookings/?customerId=customer-uuid" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceId": "service-uuid",
    "scheduledAt": "2024-01-15T10:00:00Z",
    "notes": "Please clean the kitchen thoroughly"
  }'
```

## Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/service_marketplace
SECRET_KEY=your-secret-key-change-in-production
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Database Migrations
```bash
# Initialize database
python init_db.py

# For future migrations, use Alembic
alembic init migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/` | Register user | No |
| POST | `/auth/login` | Login | No |
| GET | `/auth/me` | Get current user | Yes |
| POST | `/auth/refresh` | Refresh token | Yes |
| GET | `/users/` | List users | Yes |
| GET | `/users/{email}` | Get user by email | Yes |
| GET | `/services/` | List services | No |
| GET | `/services/{id}` | Get service | No |
| POST | `/services/` | Create service | No |
| PUT | `/services/{id}` | Update service | No |
| DELETE | `/services/{id}` | Delete service | No |
| GET | `/bookings/` | List bookings | No |
| GET | `/bookings/{id}` | Get booking | No |
| POST | `/bookings/` | Create booking | No |
| PUT | `/bookings/{id}` | Update booking | No |
| DELETE | `/bookings/{id}` | Delete booking | No |
| GET | `/health` | Health check | No |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.