from typing import Optional
import secrets
import string
from datetime import datetime, timezone

from models import User, PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetToken
from repositories.password_reset_repository import PasswordResetRepository
from repositories.users_repository import UsersRepository
from services.email_service import EmailService
from auth import get_password_hash

from sqlalchemy import text, update


class PasswordResetService:
    def __init__(self, reset_repo: PasswordResetRepository, users_repo: UsersRepository) -> None:
        self.reset_repo = reset_repo
        self.users_repo = users_repo
        self.email_service = EmailService()

    def request_password_reset(self, request: PasswordResetRequest) -> bool:
        """Request password reset - send email with reset link"""
        # Check if user exists
        user = self.users_repo.get_by_email(request.email)
        if not user:
            # Don't reveal if user exists or not for security
            return True

        # Generate secure reset token
        reset_token = self._generate_reset_token()
        
        # Create reset token in database
        try:
            self.reset_repo.create_reset_token(request.email, reset_token)
            
            # Send password reset email
            self.email_service.send_password_reset_email(user, reset_token)
            return True
        except Exception as e:
            print(f"Error creating password reset: {e}")
            return False

    def confirm_password_reset(self, request: PasswordResetConfirmRequest) -> bool:
        """Confirm password reset with token and new password"""
        # Get valid token
        reset_token = self.reset_repo.get_valid_token(request.token)
        if not reset_token:
            return False

        # Get user
        user = self.users_repo.get_by_email(reset_token.email)
        if not user:
            return False

        # Update user password
        try:
            hashed_password = get_password_hash(request.new_password)
            
            # Update password in database
            
            query = update(text("users")).where(text("email = :email")).values(
                password=hashed_password,
                updated_at=datetime.now(timezone.utc)
            )
            self.users_repo.db.execute(query, {"email": reset_token.email})
            self.users_repo.db.commit()

            # Mark token as used
            self.reset_repo.mark_token_as_used(request.token)

            # Send confirmation email
            self.email_service.send_password_reset_confirmation(user)
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    def _generate_reset_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        return self.reset_repo.cleanup_expired_tokens()
