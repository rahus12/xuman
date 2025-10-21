from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError

from models import User, UserRole
from logging_config import get_logger, log_database_operation


class UsersRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("users_repository")

    def list_users(self, role: Optional[UserRole] = None) -> List[User]:
        self.logger.info("Querying users from database", role_filter=role)
        # Using SQLAlchemy Core for type safety and SQL injection prevention
        query = select(text("*")).select_from(text("users"))
        if role is not None:
            query = query.where(text("role = :role"))
            result = self.db.execute(query, {"role": role.value})
        else:
            result = self.db.execute(query)
        
        users = [self._row_to_model(row) for row in result]
        self.logger.info("Users retrieved from database", count=len(users), role_filter=role)
        return users

    def get_by_email(self, email: str) -> Optional[User]:
        self.logger.info("Querying user by email", email=email)
        # Input validation
        if not email or not isinstance(email, str):
            self.logger.error("Invalid email provided", email=email)
            raise ValueError("Email must be a non-empty string")
        
        # Parameterized query - safe from SQL injection
        query = select(text("*")).select_from(text("users")).where(text("email = :email"))
        result = self.db.execute(query, {"email": email.lower().strip()}).fetchone()
        
        if result:
            user = self._row_to_model(result)
            self.logger.info("User found in database", user_id=user.id, email=email)
            return user
        else:
            self.logger.warning("User not found in database", email=email)
            return None

    def create_user(self, user: User) -> User:
        self.logger.info("Creating user in database", user_id=user.id, email=user.email, role=user.role)
        try:
            # Using raw SQL with parameters
            query = text("""
                INSERT INTO users (id, email, password, role, profile, created_at, updated_at)
                VALUES (:id, :email, :password, :role, :profile, :created_at, :updated_at)
            """)

            # Handle profile serialization properly
            if hasattr(user.profile, 'model_dump_json'):
                profile_json = user.profile.model_dump_json()
            else:
                import json
                profile_json = json.dumps(user.profile)
            
            self.db.execute(query, {
                "id": user.id,
                "email": user.email.lower(),
                "password": user.password,
                "role": user.role.value,
                "profile": profile_json,
                "created_at": user.createdAt,
                "updated_at": user.updatedAt
            })
            self.db.commit()
            self.logger.info("User created successfully in database", user_id=user.id, email=user.email)
            return user
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error("User creation failed - integrity error", user_id=user.id, email=user.email, error=str(e))
            raise ValueError(f"User with email {user.email} already exists") from e

    def _row_to_model(self, row) -> User:
        from models import UserProfile
        import json
        
        # Handle profile deserialization properly
        if isinstance(row.profile, str):
            profile_data = json.loads(row.profile)
        else:
            profile_data = row.profile
        
        return User(
            id=str(row.id),
            email=row.email,
            password=row.password,
            role=UserRole(row.role),
            profile=UserProfile(**profile_data),
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        )


