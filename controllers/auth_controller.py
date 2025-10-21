from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from models import LoginRequest, TokenResponse, UserResponse
from services.users_service import UsersService
from repositories.users_repository import UsersRepository
from database import get_db
from auth import create_access_token, authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from logging_config import get_logger, log_api_request, log_security_event
from rate_limiter import login_rate_limit

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_users_service(db: Session = Depends(get_db)) -> UsersService:
    return UsersService(UsersRepository(db))


@router.post("/login", response_model=TokenResponse)
@login_rate_limit()
async def login(
    request: Request,
    login_data: LoginRequest, 
    service: UsersService = Depends(get_users_service)
):
    """Login user and return JWT token"""
    logger = get_logger("auth_controller")
    
    try:
        logger.info("Login attempt", email=login_data.email)
        
        user = service.verify_user_password(login_data.email, login_data.password)
        
        if not user:
            logger.warning("Login failed - invalid credentials", email=login_data.email)
            log_security_event("login_failed", user_email=login_data.email, reason="invalid_credentials")
            log_api_request(
                method="POST",
                path=str(request.url.path),
                status_code=401,
                user_email=login_data.email
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        log_security_event("login_success", user_id=user.id, user_email=user.email)
        log_api_request(
            method="POST",
            path=str(request.url.path),
            status_code=200,
            user_id=user.id,
            user_email=user.email
        )
        
        logger.info("Login successful", user_id=user.id, email=user.email, role=user.role)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e), email=login_data.email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
