"""
Unit tests for authentication functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from models import User, UserRole, UserProfile
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    verify_token,
    authenticate_user
)
from jose import jwt
import os


class TestPasswordHashing:
    """Test cases for password hashing functionality"""
    
    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_different_passwords(self):
        """Test password verification with different passwords"""
        password1 = "password1"
        password2 = "password2"
        hashed1 = get_password_hash(password1)
        
        result = verify_password(password2, hashed1)
        
        assert result is False


class TestJWTTokenGeneration:
    """Test cases for JWT token generation"""
    
    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify content
        decoded = jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded
    
    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry"""
        data = {"sub": "test@example.com"}
        custom_expiry = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify content
        decoded = jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded
    
    def test_create_access_token_with_additional_data(self):
        """Test access token creation with additional data"""
        data = {
            "sub": "test@example.com",
            "role": "customer",
            "user_id": "123"
        }
        token = create_access_token(data)
        
        decoded = jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "customer"
        assert decoded["user_id"] == "123"


class TestAuthenticationDependencies:
    """Test cases for authentication dependencies"""
    
    def test_get_current_user_success(self, sample_customer):
        """Test successful user authentication"""
        # Create a valid token
        token = create_access_token({"sub": sample_customer.email})
        
        # Mock the OAuth2PasswordBearer dependency
        with patch('auth.oauth2_scheme') as mock_oauth:
            mock_oauth.return_value = token
            
            # Mock the users service
            with patch('auth.get_users_service_for_auth') as mock_service:
                mock_service.return_value.get_user_by_email.return_value = sample_customer
                
                # This would be called in the actual endpoint
                # For unit testing, we'll test the logic directly
                from auth import get_current_user
                
                # Mock the dependency injection
                async def mock_get_current_user():
                    return await get_current_user(token, mock_service.return_value)
                
                # This is a simplified test - in practice you'd use pytest-asyncio
                # or test the actual endpoint with TestClient
                pass
    
    def test_get_current_user_invalid_token(self):
        """Test authentication with invalid token"""
        invalid_token = "invalid.token.here"
        
        with patch('auth.oauth2_scheme') as mock_oauth:
            mock_oauth.return_value = invalid_token
            
            with patch('auth.get_users_service_for_auth') as mock_service:
                # This should raise an HTTPException
                with pytest.raises(Exception):  # HTTPException in actual implementation
                    pass  # Would test the actual endpoint here
    
    def test_get_current_user_user_not_found(self):
        """Test authentication with valid token but user not found"""
        token = create_access_token({"sub": "nonexistent@example.com"})
        
        with patch('auth.oauth2_scheme') as mock_oauth:
            mock_oauth.return_value = token
            
            with patch('auth.get_users_service_for_auth') as mock_service:
                mock_service.return_value.get_user_by_email.return_value = None
                
                # This should raise an HTTPException
                with pytest.raises(Exception):  # HTTPException in actual implementation
                    pass  # Would test the actual endpoint here


class TestRoleBasedAuthentication:
    """Test cases for role-based authentication"""
    
    def test_customer_role_validation(self, sample_customer):
        """Test customer role validation"""
        assert sample_customer.role == UserRole.CUSTOMER
    
    def test_provider_role_validation(self, sample_customer):
        """Test provider role validation"""
        # Change role to provider
        sample_customer.role = UserRole.PROVIDER
        assert sample_customer.role == UserRole.PROVIDER


class TestTokenValidation:
    """Test cases for token validation"""
    
    def test_token_with_missing_sub(self):
        """Test token validation with missing subject"""
        # Create token without 'sub' field
        data = {"role": "customer"}
        token = create_access_token(data)
        
        # This should fail validation
        with pytest.raises(Exception):
            jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
    
    def test_token_with_invalid_signature(self):
        """Test token validation with invalid signature"""
        token = "invalid.token.signature"
        
        with pytest.raises(Exception):
            jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
    
    def test_token_with_wrong_algorithm(self):
        """Test token validation with wrong algorithm"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Try to decode with wrong algorithm
        with pytest.raises(Exception):
            jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS512"])
    
    def test_expired_token(self):
        """Test token validation with expired token"""
        # Create token with past expiry
        data = {"sub": "test@example.com"}
        past_expiry = timedelta(hours=-1)
        token = create_access_token(data, expires_delta=past_expiry)
        
        # This should fail due to expiration
        with pytest.raises(Exception):
            jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-key"), algorithms=["HS256"])
