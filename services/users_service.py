from typing import List, Optional

from models import User, UserCreateRequest, UserResponse, UserRole
from repositories.users_repository import UsersRepository
from auth import get_password_hash, verify_password
from logging_config import get_logger, log_database_operation, log_business_event

'''
DO NOT REMOVE THIS COMMENT.
Need to add authorizations rules.
Need to add password reset functionality.
'''

class UsersService:
    def __init__(self, repository: UsersRepository) -> None:
        self.repository = repository
        self.logger = get_logger("users_service")

    def list_users(self, role: Optional[UserRole] = None) -> List[UserResponse]:
        self.logger.info("Listing users", role_filter=role)
        users = self.repository.list_users(role)
        log_database_operation("SELECT", "users", filters={"role": str(role) if role else None})
        self.logger.info("Users retrieved", count=len(users), role_filter=role)
        return [self._to_response(u) for u in users]

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        self.logger.info("Getting user by email", email=email)
        u = self.repository.get_by_email(email)
        log_database_operation("SELECT", "users", filters={"email": email})
        
        if u:
            self.logger.info("User found", user_id=u.id, email=email)
            return self._to_response(u)
        else:
            self.logger.warning("User not found", email=email)
            return None

    def create_user(self, payload: UserCreateRequest) -> Optional[UserResponse]:
        self.logger.info("Creating user", email=payload.email, role=payload.role)
        
        # Check if user already exists
        existing_user = self.repository.get_by_email(payload.email)
        if existing_user:
            self.logger.warning("User creation failed - email already exists", email=payload.email)
            return None
        
        try:
            hashed = get_password_hash(payload.password)
            user = User(
                email=payload.email,
                password=hashed,
                role=payload.role,
                profile=payload.profile,
            )
            created = self.repository.create_user(user)
            log_database_operation("INSERT", "users", record_id=created.id)
            log_business_event("user_created", "user", created.id, email=payload.email, role=payload.role)
            self.logger.info("User created successfully", user_id=created.id, email=payload.email, role=payload.role)
            return self._to_response(created)
        except ValueError as e:
            # Handle duplicate email error from repository
            if "already exists" in str(e):
                self.logger.warning("User creation failed - duplicate email", email=payload.email, error=str(e))
                return None
            self.logger.error("User creation failed", email=payload.email, error=str(e))
            raise e

    def verify_user_password(self, email: str, password: str) -> Optional[User]:
        """Verify user password for authentication"""
        self.logger.info("Verifying user password", email=email)
        user = self.repository.get_by_email(email)
        if not user:
            self.logger.warning("Password verification failed - user not found", email=email)
            return None
        if not verify_password(password, user.password):
            self.logger.warning("Password verification failed - invalid password", email=email, user_id=user.id)
            return None
        self.logger.info("Password verification successful", email=email, user_id=user.id)
        return user

    def _to_response(self, u: User) -> UserResponse:
        return UserResponse(
            id=u.id,
            email=u.email,
            role=u.role,
            profile=u.profile,
            createdAt=u.createdAt,
            updatedAt=u.updatedAt,
        )


