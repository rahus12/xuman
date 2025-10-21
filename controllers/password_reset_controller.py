from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import PasswordResetRequest, PasswordResetConfirmRequest
from services.password_reset_service import PasswordResetService
from repositories.password_reset_repository import PasswordResetRepository
from repositories.users_repository import UsersRepository
from database import get_db

router = APIRouter(prefix="/password-reset", tags=["password-reset"])


def get_password_reset_service(db: Session = Depends(get_db)) -> PasswordResetService:
    return PasswordResetService(
        PasswordResetRepository(db),
        UsersRepository(db)
    )


@router.post("/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: PasswordResetRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """
    Request password reset - sends email with reset link
    Always returns 200 for security (doesn't reveal if email exists)
    """
    success = service.request_password_reset(request)
    return {
        "message": "If the email exists in our system, you will receive a password reset link.",
        "success": success
    }


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """
    Confirm password reset with token and new password
    """
    success = service.confirm_password_reset(request)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {
        "message": "Password has been successfully reset",
        "success": True
    }


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_tokens(
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """
    Clean up expired password reset tokens (admin endpoint)
    """
    cleaned_count = service.cleanup_expired_tokens()
    return {
        "message": f"Cleaned up {cleaned_count} expired tokens",
        "cleaned_count": cleaned_count
    }
