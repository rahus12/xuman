"""
Unit tests for password reset functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from models import User, UserRole, UserProfile, PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetToken
from services.password_reset_service import PasswordResetService
from repositories.password_reset_repository import PasswordResetRepository
from repositories.users_repository import UsersRepository


class TestPasswordResetService:
    """Test cases for PasswordResetService"""
    
    def test_request_password_reset_success(self, db_session, sample_customer):
        """Test successful password reset request"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Mock user exists
        with patch.object(users_repo, 'get_by_email', return_value=sample_customer):
            with patch.object(service.email_service, 'send_password_reset_email'):
                request = PasswordResetRequest(email=sample_customer.email)
                result = service.request_password_reset(request)
        
        assert result is True
    
    def test_request_password_reset_user_not_found(self, db_session):
        """Test password reset request for non-existent user"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Mock user doesn't exist
        with patch.object(users_repo, 'get_by_email', return_value=None):
            request = PasswordResetRequest(email="nonexistent@test.com")
            result = service.request_password_reset(request)
        
        # Should still return True for security (doesn't reveal if user exists)
        assert result is True
    
    def test_request_password_reset_database_error(self, db_session, sample_customer):
        """Test password reset request with database error"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Mock user exists but database error occurs
        with patch.object(users_repo, 'get_by_email', return_value=sample_customer):
            with patch.object(reset_repo, 'create_reset_token', side_effect=Exception("Database error")):
                request = PasswordResetRequest(email=sample_customer.email)
                result = service.request_password_reset(request)
        
        assert result is False
    
    def test_confirm_password_reset_success(self, db_session, sample_customer):
        """Test successful password reset confirmation"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Create a valid reset token
        reset_token = PasswordResetToken(
            email=sample_customer.email,
            token="valid_reset_token",
            expiresAt=datetime.now(timezone.utc) + timedelta(hours=24),
            isUsed=False
        )
        
        # Mock repository methods
        with patch.object(reset_repo, 'get_valid_token', return_value=reset_token):
            with patch.object(users_repo, 'get_by_email', return_value=sample_customer):
                with patch('services.password_reset_service.get_password_hash', return_value="new_hashed_password"):
                    with patch.object(users_repo.db, 'execute'):
                        with patch.object(users_repo.db, 'commit'):
                            with patch.object(reset_repo, 'mark_token_as_used', return_value=True):
                                with patch.object(service.email_service, 'send_password_reset_confirmation'):
                                    request = PasswordResetConfirmRequest(
                                        token="valid_reset_token",
                                        new_password="newpassword123"
                                    )
                                    result = service.confirm_password_reset(request)
        
        assert result is True
    
    def test_confirm_password_reset_invalid_token(self, db_session):
        """Test password reset confirmation with invalid token"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Mock invalid token
        with patch.object(reset_repo, 'get_valid_token', return_value=None):
            request = PasswordResetConfirmRequest(
                token="invalid_token",
                new_password="newpassword123"
            )
            result = service.confirm_password_reset(request)
        
        assert result is False
    
    def test_confirm_password_reset_expired_token(self, db_session, sample_customer):
        """Test password reset confirmation with expired token"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Create expired reset token
        expired_token = PasswordResetToken(
            email=sample_customer.email,
            token="expired_token",
            expiresAt=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            isUsed=False
        )
        
        # Mock expired token (get_valid_token should return None for expired)
        with patch.object(reset_repo, 'get_valid_token', return_value=None):
            request = PasswordResetConfirmRequest(
                token="expired_token",
                new_password="newpassword123"
            )
            result = service.confirm_password_reset(request)
        
        assert result is False
    
    def test_confirm_password_reset_used_token(self, db_session, sample_customer):
        """Test password reset confirmation with already used token"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Mock used token (get_valid_token should return None for used tokens)
        with patch.object(reset_repo, 'get_valid_token', return_value=None):
            request = PasswordResetConfirmRequest(
                token="used_token",
                new_password="newpassword123"
            )
            result = service.confirm_password_reset(request)
        
        assert result is False
    
    def test_confirm_password_reset_user_not_found(self, db_session):
        """Test password reset confirmation with user not found"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        # Create valid token but user not found
        reset_token = PasswordResetToken(
            email="nonexistent@test.com",
            token="valid_reset_token",
            expiresAt=datetime.now(timezone.utc) + timedelta(hours=24),
            isUsed=False
        )
        
        with patch.object(reset_repo, 'get_valid_token', return_value=reset_token):
            with patch.object(users_repo, 'get_by_email', return_value=None):
                request = PasswordResetConfirmRequest(
                    token="valid_reset_token",
                    new_password="newpassword123"
                )
                result = service.confirm_password_reset(request)
        
        assert result is False
    
    def test_generate_reset_token(self, db_session):
        """Test reset token generation"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        token = service._generate_reset_token()
        
        assert isinstance(token, str)
        assert len(token) == 32  # Default length
        assert token.isalnum()  # Should contain only alphanumeric characters
    
    def test_generate_reset_token_custom_length(self, db_session):
        """Test reset token generation with custom length"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        token = service._generate_reset_token(length=16)
        
        assert isinstance(token, str)
        assert len(token) == 16
        assert token.isalnum()
    
    def test_cleanup_expired_tokens(self, db_session):
        """Test cleanup of expired tokens"""
        reset_repo = PasswordResetRepository(db_session)
        users_repo = UsersRepository(db_session)
        service = PasswordResetService(reset_repo, users_repo)
        
        with patch.object(reset_repo, 'cleanup_expired_tokens', return_value=5):
            result = service.cleanup_expired_tokens()
        
        assert result == 5


class TestPasswordResetRepository:
    """Test cases for PasswordResetRepository"""
    
    def test_create_reset_token_success(self, db_session):
        """Test successful reset token creation"""
        repo = PasswordResetRepository(db_session)
        
        with patch('repositories.password_reset_repository.uuid.uuid4', return_value="test-token-id"):
            with patch('repositories.password_reset_repository.datetime.now', return_value=datetime.now(timezone.utc)):
                result = repo.create_reset_token("test@example.com", "test_token", 24)
        
        assert result is not None
        assert result.email == "test@example.com"
        assert result.token == "test_token"
        assert result.isUsed is False
    
    def test_get_valid_token_success(self, db_session):
        """Test successful valid token retrieval"""
        repo = PasswordResetRepository(db_session)
        
        # Create a valid token
        valid_token = PasswordResetToken(
            email="test@example.com",
            token="valid_token",
            expiresAt=datetime.now(timezone.utc) + timedelta(hours=24),
            isUsed=False
        )
        
        with patch.object(db_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.fetchone.return_value = MagicMock(
                id=valid_token.id,
                email=valid_token.email,
                token=valid_token.token,
                expires_at=valid_token.expiresAt,
                is_used=valid_token.isUsed,
                created_at=valid_token.createdAt
            )
            mock_execute.return_value = mock_result
            
            result = repo.get_valid_token("valid_token")
        
        assert result is not None
        assert result.token == "valid_token"
    
    def test_get_valid_token_not_found(self, db_session):
        """Test valid token retrieval for non-existent token"""
        repo = PasswordResetRepository(db_session)
        
        with patch.object(db_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None
            mock_execute.return_value = mock_result
            
            result = repo.get_valid_token("invalid_token")
        
        assert result is None
    
    def test_mark_token_as_used_success(self, db_session):
        """Test successful token marking as used"""
        repo = PasswordResetRepository(db_session)
        
        with patch.object(db_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.rowcount = 1
            mock_execute.return_value = mock_result
            
            result = repo.mark_token_as_used("test_token")
        
        assert result is True
    
    def test_mark_token_as_used_not_found(self, db_session):
        """Test token marking as used for non-existent token"""
        repo = PasswordResetRepository(db_session)
        
        with patch.object(db_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.rowcount = 0
            mock_execute.return_value = mock_result
            
            result = repo.mark_token_as_used("invalid_token")
        
        assert result is False
    
    def test_cleanup_expired_tokens(self, db_session):
        """Test cleanup of expired tokens"""
        repo = PasswordResetRepository(db_session)
        
        with patch.object(db_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.rowcount = 3
            mock_execute.return_value = mock_result
            
            result = repo.cleanup_expired_tokens()
        
        assert result == 3
