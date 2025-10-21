"""
Unit tests for authentication functionality
Tests JWT token generation, validation, and user authentication
"""
import pytest
from datetime import datetime, timedelta
from models import User, UserRole, UserProfile
from auth import authenticate_user, create_access_token
from repositories.users_repository import UsersRepository


class TestAuthentication:
    """Test authentication and JWT token handling"""
    
    def test_successful_authentication_consumer(self, test_db, sample_consumer):
        """Test consumer can be authenticated with correct credentials"""
        users_repo = UsersRepository(test_db)
        
        user = authenticate_user("consumer123@example.com", "password123", users_repo)
        
        assert user is not None
        assert user.email == "consumer123@example.com"
        assert user.role == UserRole.CUSTOMER
    
    def test_successful_authentication_provider(self, test_db, sample_provider):
        """Test provider can be authenticated with correct credentials"""
        users_repo = UsersRepository(test_db)
        
        user = authenticate_user("provider123@example.com", "password123", users_repo)
        
        assert user is not None
        assert user.email == "provider123@example.com"
        assert user.role == UserRole.PROVIDER
    
    def test_authentication_with_wrong_password(self, test_db, sample_consumer):
        """Test authentication fails with incorrect password"""
        users_repo = UsersRepository(test_db)
        
        user = authenticate_user("consumer123@example.com", "wrongpassword", users_repo)
        
        assert user is None
    
    def test_authentication_with_nonexistent_email(self, test_db):
        """Test authentication fails with non-existent email"""
        users_repo = UsersRepository(test_db)
        
        user = authenticate_user("nonexistent@example.com", "password123", users_repo)
        
        assert user is None
    
    def test_create_access_token(self, sample_consumer):
        """Test JWT token creation"""
        from datetime import timedelta
        
        token = create_access_token(
            data={"sub": sample_consumer.email},
            expires_delta=timedelta(minutes=30)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_user_info(self, sample_consumer):
        """Test JWT token contains correct user information"""
        from datetime import timedelta
        from jose import jwt
        import os
        
        token = create_access_token(
            data={"sub": sample_consumer.email},
            expires_delta=timedelta(minutes=30)
        )
        
        # Decode token to verify claims
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        assert payload["sub"] == sample_consumer.email
        assert "exp" in payload
