import pytest
from unittest.mock import patch
from models import User, UserCreateRequest, UserRole, UserProfile, UserResponse
from repositories.users_repository import UsersRepository
from services.users_service import UsersService
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone

class TestUserService:
    """Test cases for UsersService"""

    def test_create_user_success(self, db_session, sample_customer_profile):
        """Test successful user creation"""
        service = UsersService(UsersRepository(db_session))

        from models import UserCreateRequest
        user_data = UserCreateRequest(
            email="newuser@test.com",
            password="password123",
            role=UserRole.CUSTOMER,
            profile=sample_customer_profile
        )

        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            result = service.create_user(user_data)

        assert result is not None
        assert result.email == "newuser@test.com"
        assert result.role == UserRole.CUSTOMER
        assert result.profile.firstName == sample_customer_profile.firstName

    def test_create_user_duplicate_email(self, db_session, sample_customer_profile):
        """Test user creation with duplicate email"""
        service = UsersService(UsersRepository(db_session))

        from models import UserCreateRequest
        user_data = UserCreateRequest(
            email="duplicate@test.com",
            password="password123",
            role=UserRole.CUSTOMER,
            profile=sample_customer_profile
        )

        # Create first user
        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            service.create_user(user_data)

        # Try to create second user with same email
        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            result = service.create_user(user_data)

        assert result is None  # Should return None for duplicate email

    def test_get_user_by_email_success(self, db_session, sample_customer):
        """Test getting user by email"""
        service = UsersService(UsersRepository(db_session))

        # Create user in database
        from models import UserCreateRequest
        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            service.create_user(UserCreateRequest(
                email=sample_customer.email,
                password="password123",
                role=sample_customer.role,
                profile=sample_customer.profile
            ))

        result = service.get_user_by_email(sample_customer.email)

        assert result is not None
        assert result.email == sample_customer.email

    def test_get_user_by_email_not_found(self, db_session):
        """Test getting a non-existent user by email"""
        service = UsersService(UsersRepository(db_session))
        result = service.get_user_by_email("nonexistent@test.com")
        assert result is None

    def test_list_users_all(self, db_session, sample_customer, sample_provider):
        """Test listing all users"""
        service = UsersService(UsersRepository(db_session))

        # Create users in database
        from models import UserCreateRequest
        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            service.create_user(UserCreateRequest(
                email=sample_customer.email,
                password="password123",
                role=sample_customer.role,
                profile=sample_customer.profile
            ))
            service.create_user(UserCreateRequest(
                email=sample_provider.email,
                password="password123",
                role=sample_provider.role,
                profile=sample_provider.profile
            ))

        users = service.list_users()
        assert len(users) == 2
        assert any(u.email == sample_customer.email for u in users)
        assert any(u.email == sample_provider.email for u in users)

    def test_list_users_by_role(self, db_session, sample_customer, sample_provider):
        """Test listing users by role"""
        service = UsersService(UsersRepository(db_session))

        # Create users in database
        from models import UserCreateRequest
        with patch('services.users_service.get_password_hash', return_value="hashed_password"):
            service.create_user(UserCreateRequest(
                email=sample_customer.email,
                password="password123",
                role=sample_customer.role,
                profile=sample_customer.profile
            ))
            service.create_user(UserCreateRequest(
                email=sample_provider.email,
                password="password123",
                role=sample_provider.role,
                profile=sample_provider.profile
            ))

        customers = service.list_users(role=UserRole.CUSTOMER)
        assert len(customers) == 1
        assert customers[0].email == sample_customer.email

        providers = service.list_users(role=UserRole.PROVIDER)
        assert len(providers) == 1
        assert providers[0].email == sample_provider.email

    def test_verify_user_password_success(self, db_session, sample_customer):
        """Test successful password verification"""
        service = UsersService(UsersRepository(db_session))
        hashed_password = "hashed_password"
        with patch('services.users_service.get_password_hash', return_value=hashed_password):
            from models import UserCreateRequest
            service.create_user(UserCreateRequest(
                email=sample_customer.email,
                password="password123",
                role=sample_customer.role,
                profile=sample_customer.profile
            ))

        with patch('services.users_service.verify_password', return_value=True):
            user = service.verify_user_password(sample_customer.email, "password123")
            assert user is not None
            assert user.email == sample_customer.email

    def test_verify_user_password_wrong_password(self, db_session, sample_customer):
        """Test password verification with wrong password"""
        service = UsersService(UsersRepository(db_session))
        hashed_password = "hashed_password"
        with patch('services.users_service.get_password_hash', return_value=hashed_password):
            from models import UserCreateRequest
            service.create_user(UserCreateRequest(
                email=sample_customer.email,
                password="password123",
                role=sample_customer.role,
                profile=sample_customer.profile
            ))

        with patch('services.users_service.verify_password', return_value=False):
            user = service.verify_user_password(sample_customer.email, "wrongpassword")
            assert user is None

    def test_verify_user_password_user_not_found(self, db_session):
        """Test password verification for non-existent user"""
        service = UsersService(UsersRepository(db_session))
        user = service.verify_user_password("nonexistent@test.com", "password123")
        assert user is None


class TestUserRepository:
    """Test cases for UsersRepository"""

    def test_create_user_database_error(self, db_session, sample_customer):
        """Test database error during user creation"""
        repo = UsersRepository(db_session)
        # Simulate a database error by trying to create a user with an existing email
        # without proper error handling in the service layer, this would raise IntegrityError
        with patch.object(db_session, 'execute', side_effect=IntegrityError("mock", {}, {})):
            with pytest.raises(ValueError, match="User with email"):
                repo.create_user(sample_customer)

    def test_get_by_email_input_validation(self, db_session):
        """Test input validation for get_by_email"""
        repo = UsersRepository(db_session)
        with pytest.raises(ValueError, match="Email must be a non-empty string"):
            repo.get_by_email(None)
        with pytest.raises(ValueError, match="Email must be a non-empty string"):
            repo.get_by_email("")
        with pytest.raises(ValueError, match="Email must be a non-empty string"):
            repo.get_by_email(123)
