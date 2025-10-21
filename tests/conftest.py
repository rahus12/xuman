import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import asyncio
from main import app
from database import get_db
from models import User, UserRole, UserProfile, Service, ServiceAvailability, Booking, BookingStatus, PasswordResetToken
from datetime import datetime, timezone, timedelta
import json
from unittest.mock import patch

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
TestingEngine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestingEngine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    session = TestingSessionLocal()

    # Create tables using raw SQL
    from sqlalchemy import text

    # Create users table
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('customer', 'provider')),
            profile TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create services table
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            provider_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL CHECK (price > 0),
            currency TEXT DEFAULT 'USD',
            duration INTEGER NOT NULL CHECK (duration > 0),
            availability TEXT NOT NULL,
            images TEXT DEFAULT '[]',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create bookings table
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            service_id TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
            scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
            duration INTEGER NOT NULL CHECK (duration > 0),
            total_amount REAL NOT NULL CHECK (total_amount > 0),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create password reset tokens table
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))

    session.commit()

    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        session = TestingSessionLocal()
        session.execute(text("DROP TABLE IF EXISTS password_reset_tokens"))
        session.execute(text("DROP TABLE IF EXISTS bookings"))
        session.execute(text("DROP TABLE IF EXISTS services"))
        session.execute(text("DROP TABLE IF EXISTS users"))
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Sample data fixtures
@pytest.fixture
def sample_customer_profile():
    """Sample customer profile data"""
    return UserProfile(
        firstName="John",
        lastName="Doe",
        phone="+1234567890",
        address="123 Main St, City, State 12345"
    )


@pytest.fixture
def sample_provider_profile():
    """Sample provider profile data"""
    return UserProfile(
        firstName="Jane",
        lastName="Smith",
        phone="+0987654321",
        address="456 Oak Ave, City, State 54321"
    )


@pytest.fixture
def sample_customer(sample_customer_profile):
    """Sample customer user"""
    return User(
        id="customer-123",
        email="customer@test.com",
        password="hashed_password",
        role=UserRole.CUSTOMER,
        profile=sample_customer_profile,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_provider(sample_provider_profile):
    """Sample provider user"""
    return User(
        id="provider-123",
        email="provider@test.com",
        password="hashed_password",
        role=UserRole.PROVIDER,
        profile=sample_provider_profile,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_service_availability():
    """Sample service availability data"""
    return ServiceAvailability(
        monday=["09:00-17:00"],
        tuesday=["09:00-17:00"],
        wednesday=["09:00-17:00"],
        thursday=["09:00-17:00"],
        friday=["09:00-17:00"],
        saturday=[],
        sunday=[]
    )


@pytest.fixture
def sample_service(sample_provider, sample_service_availability):
    """Sample service"""
    return Service(
        id="service-123",
        providerId=sample_provider.id,
        title="Test Service",
        description="A test service description",
        category="consulting",
        price=100.0,
        currency="USD",
        duration=60,
        availability=sample_service_availability,
        images=["image1.jpg", "image2.jpg"],
        isActive=True,
        createdAt=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_booking(sample_customer, sample_provider, sample_service):
    """Sample booking"""
    return Booking(
        id="booking-123",
        customerId=sample_customer.id,
        serviceId=sample_service.id,
        providerId=sample_provider.id,
        status=BookingStatus.PENDING,
        scheduledAt=datetime.now(timezone.utc) + timedelta(days=1),
        duration=60,
        totalAmount=100.0,
        notes="Test booking",
        createdAt=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_password_reset_token(sample_customer):
    """Sample password reset token"""
    return PasswordResetToken(
        id="token-123",
        email=sample_customer.email,
        token="reset_token_123",
        expiresAt=datetime.now(timezone.utc) + timedelta(hours=24),
        isUsed=False,
        createdAt=datetime.now(timezone.utc)
    )
