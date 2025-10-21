"""
Pytest configuration and fixtures for testing
"""
import pytest
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment
os.environ["TESTING"] = "1"
os.environ["PAYMENT_FAILURE_RATE"] = "0.0"

from main import app
from database import get_db
from models import (
    User, UserRole, UserProfile, Service, ServiceAvailability,
    Booking, BookingStatus, PaymentMethod
)
from repositories.users_repository import UsersRepository
from repositories.services_repository import ServicesRepository
from repositories.bookings_repository import BookingsRepository
from auth import authenticate_user, create_access_token


# Test database URL (using psycopg, not psycopg2)
# Read from environment variable, fallback to local development database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://vishalchamaria@localhost:5432/marketplace_test"
)


@pytest.fixture(scope="function")
def test_db():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables manually
    with engine.connect() as conn:
        # Drop all tables
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
        
        # Create enums
        conn.execute(text("CREATE TYPE userrole AS ENUM ('CUSTOMER', 'PROVIDER')"))
        conn.execute(text("CREATE TYPE servicestatus AS ENUM ('PENDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED')"))
        conn.execute(text("CREATE TYPE bookingstatus AS ENUM ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED')"))
        conn.commit()
        
        # Create tables
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role UserRole NOT NULL,
                profile JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS services (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                provider_id UUID NOT NULL REFERENCES users(id),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL,
                duration_minutes INTEGER NOT NULL,
                availability JSONB NOT NULL DEFAULT '{}',
                status ServiceStatus DEFAULT 'PENDING',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bookings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                customer_id UUID NOT NULL REFERENCES users(id),
                service_id UUID NOT NULL REFERENCES services(id),
                provider_id UUID NOT NULL REFERENCES users(id),
                status BookingStatus DEFAULT 'PENDING',
                scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
                duration_minutes INTEGER NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                booking_id UUID NOT NULL REFERENCES bookings(id),
                status VARCHAR(50) NOT NULL,
                transaction_id VARCHAR(255) UNIQUE NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                currency VARCHAR(10) NOT NULL,
                payment_method JSONB NOT NULL,
                failure_reason TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notifications (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data JSONB,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        conn.commit()
    
    # Create session
    session = TestSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_consumer(test_db):
    """Create a sample consumer user"""
    from services.users_service import UsersService
    from models import UserCreateRequest
    
    users_repo = UsersRepository(test_db)
    users_service = UsersService(users_repo)
    
    user_request = UserCreateRequest(
        email="consumer123@example.com",
        password="password123",  # Plaintext - will be hashed by service
        role=UserRole.CUSTOMER,
        profile=UserProfile(
            firstName="Jane",
            lastName="Consumer",
            phone="+1234567890",
            address="123 Consumer St"
        )
    )
    
    created_user_response = users_service.create_user(user_request)
    # Get the actual user object from repository
    created_user = users_repo.get_by_email("consumer123@example.com")
    return created_user


@pytest.fixture
def sample_provider(test_db):
    """Create a sample provider user"""
    from services.users_service import UsersService
    from models import UserCreateRequest
    
    users_repo = UsersRepository(test_db)
    users_service = UsersService(users_repo)
    
    user_request = UserCreateRequest(
        email="provider123@example.com",
        password="password123",  # Plaintext - will be hashed by service
        role=UserRole.PROVIDER,
        profile=UserProfile(
            firstName="John",
            lastName="Provider",
            phone="+1234567891",
            address="456 Provider Ave"
        )
    )
    
    created_user_response = users_service.create_user(user_request)
    created_user = users_repo.get_by_email("provider123@example.com")
    return created_user


@pytest.fixture
def other_consumer(test_db):
    """Create another consumer user"""
    from services.users_service import UsersService
    from models import UserCreateRequest
    
    users_repo = UsersRepository(test_db)
    users_service = UsersService(users_repo)
    
    user_request = UserCreateRequest(
        email="otherconsumer@example.com",
        password="password123",  # Plaintext - will be hashed by service
        role=UserRole.CUSTOMER,
        profile=UserProfile(
            firstName="Other",
            lastName="Consumer",
            phone="+1234567892",
            address="789 Other St"
        )
    )
    
    created_user_response = users_service.create_user(user_request)
    created_user = users_repo.get_by_email("otherconsumer@example.com")
    return created_user


@pytest.fixture
def other_provider(test_db):
    """Create another provider user"""
    from services.users_service import UsersService
    from models import UserCreateRequest
    
    users_repo = UsersRepository(test_db)
    users_service = UsersService(users_repo)
    
    user_request = UserCreateRequest(
        email="otherprovider@example.com",
        password="password123",  # Plaintext - will be hashed by service
        role=UserRole.PROVIDER,
        profile=UserProfile(
            firstName="Other",
            lastName="Provider",
            phone="+1234567893",
            address="321 Other Ave"
        )
    )
    
    created_user_response = users_service.create_user(user_request)
    created_user = users_repo.get_by_email("otherprovider@example.com")
    return created_user


@pytest.fixture
def sample_service(test_db, sample_provider):
    """Create a sample service"""
    services_repo = ServicesRepository(test_db)
    
    service = Service(
        providerId=sample_provider.id,
        name="Test Service",
        description="Test service description",
        price=100.0,
        durationMinutes=60,
        availability=ServiceAvailability(
            monday=["09:00", "17:00"],
            wednesday=["09:00", "17:00"],
            friday=["09:00", "17:00"]
        ),
        status="ACTIVE"
    )
    
    created_service = services_repo.create_service(service)
    return created_service


@pytest.fixture
def sample_booking(test_db, sample_consumer, sample_service):
    """Create a sample booking"""
    bookings_repo = BookingsRepository(test_db)
    
    booking = Booking(
        customerId=sample_consumer.id,
        serviceId=sample_service.id,
        providerId=sample_service.providerId,
        status=BookingStatus.CONFIRMED,
        scheduledAt=datetime.now(timezone.utc) + timedelta(days=7),
        duration=sample_service.durationMinutes,
        totalAmount=sample_service.price,
        notes="Sample booking"
    )
    
    created_booking = bookings_repo.create_booking(booking)
    return created_booking


@pytest.fixture
def consumer_token(client, sample_consumer):
    """Get authentication token for consumer"""
    response = client.post("/auth/login", json={
        "email": "consumer123@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def provider_token(client, sample_provider):
    """Get authentication token for provider"""
    response = client.post("/auth/login", json={
        "email": "provider123@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def other_consumer_token(client, other_consumer):
    """Get authentication token for other consumer"""
    response = client.post("/auth/login", json={
        "email": "otherconsumer@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def other_provider_token(client, other_provider):
    """Get authentication token for other provider"""
    response = client.post("/auth/login", json={
        "email": "otherprovider@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]
