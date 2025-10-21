from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from models import UserCreateRequest, UserResponse, UserRole
from repositories.users_repository import UsersRepository
from services.users_service import UsersService
from database import get_db
from auth import get_current_user
from logging_config import get_logger, log_api_request, log_security_event, log_business_event

router = APIRouter(prefix="/users", tags=["users"])


def get_users_layer(db: Session = Depends(get_db)) -> UsersService:
    return UsersService(UsersRepository(db))

'''
DO NOT REMOVE THIS COMMENT.
Need to add authorizations rules.
'''

@router.get("/", response_model=List[UserResponse])
async def list_users(
    request: Request,
    role: Optional[UserRole] = Query(None), 
    service: UsersService = Depends(get_users_layer),
    current_user: UserResponse = Depends(get_current_user)
):
    """List users - requires authentication"""
    logger = get_logger("users_controller")
    
    try:
        logger.info("Listing users", user_id=current_user.id, role_filter=role)
        users = service.list_users(role)
        
        log_api_request(
            method="GET",
            path=str(request.url.path),
            status_code=200,
            user_id=current_user.id,
            query_params={"role": str(role) if role else None}
        )
        
        logger.info("Users listed successfully", count=len(users), user_id=current_user.id)
        return users
        
    except Exception as e:
        logger.error("Failed to list users", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{email}", response_model=UserResponse)
async def get_user(
    request: Request,
    email: str, 
    service: UsersService = Depends(get_users_layer),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user by email - requires authentication"""
    logger = get_logger("users_controller")
    
    try:
        logger.info("Getting user by email", requested_email=email, user_id=current_user.id)
        result = service.get_user_by_email(email)
        
        if not result:
            logger.warning("User not found", requested_email=email, user_id=current_user.id)
            log_api_request(
                method="GET",
                path=str(request.url.path),
                status_code=404,
                user_id=current_user.id,
                requested_email=email
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_api_request(
            method="GET",
            path=str(request.url.path),
            status_code=200,
            user_id=current_user.id,
            requested_email=email
        )
        
        logger.info("User retrieved successfully", requested_email=email, user_id=current_user.id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", error=str(e), requested_email=email, user_id=current_user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    payload: UserCreateRequest, 
    service: UsersService = Depends(get_users_layer)
):
    """Register new user - no authentication required"""
    logger = get_logger("users_controller")
    
    try:
        logger.info("User registration attempt", email=payload.email, role=payload.role)
        
        result = service.create_user(payload)
        
        if not result:
            logger.warning("User registration failed - email already exists", email=payload.email)
            log_security_event("registration_failed", user_email=payload.email, reason="email_already_exists")
            log_api_request(
                method="POST",
                path=str(request.url.path),
                status_code=400,
                user_email=payload.email
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        
        log_business_event("user_created", "user", result.id, email=payload.email, role=payload.role)
        log_security_event("user_registered", user_id=result.id, user_email=payload.email)
        log_api_request(
            method="POST",
            path=str(request.url.path),
            status_code=201,
            user_id=result.id,
            user_email=payload.email
        )
        
        logger.info("User registered successfully", user_id=result.id, email=payload.email, role=payload.role)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("User registration failed", error=str(e), email=payload.email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


