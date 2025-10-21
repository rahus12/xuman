from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone, timedelta

from models import PasswordResetToken


class PasswordResetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_reset_token(self, email: str, token: str, expires_in_hours: int = 24) -> PasswordResetToken:
        """Create a new password reset token"""
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
            reset_token = PasswordResetToken(
                email=email,
                token=token,
                expiresAt=expires_at
            )
            
            query = text("""
                INSERT INTO password_reset_tokens (id, email, token, expires_at, is_used, created_at)
                VALUES (:id, :email, :token, :expires_at, :is_used, :created_at)
            """)

            self.db.execute(query, {
                "id": reset_token.id,
                "email": reset_token.email.lower(),
                "token": reset_token.token,
                "expires_at": reset_token.expiresAt,
                "is_used": reset_token.isUsed,
                "created_at": reset_token.createdAt
            })
            self.db.commit()
            return reset_token
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error creating reset token: {e}") from e

    def get_valid_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get a valid (not expired and not used) reset token"""
        query = text("""
            SELECT * FROM password_reset_tokens 
            WHERE token = :token AND is_used = false AND expires_at > :now
        """)
        result = self.db.execute(query, {
            "token": token,
            "now": datetime.now(timezone.utc)
        }).fetchone()
        return self._row_to_model(result) if result else None

    def mark_token_as_used(self, token: str) -> bool:
        """Mark a token as used"""
        query = text("""
            UPDATE password_reset_tokens 
            SET is_used = true 
            WHERE token = :token
        """)
        
        result = self.db.execute(query, {"token": token})
        self.db.commit()
        return result.rowcount > 0

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        query = text("""
            DELETE FROM password_reset_tokens 
            WHERE expires_at < :now
        """)
        result = self.db.execute(query, {"now": datetime.now(timezone.utc)})
        self.db.commit()
        return result.rowcount

    def _row_to_model(self, row) -> PasswordResetToken:
        return PasswordResetToken(
            id=str(row.id),
            email=row.email,
            token=row.token,
            expiresAt=row.expires_at,
            isUsed=row.is_used,
            createdAt=row.created_at,
        )
