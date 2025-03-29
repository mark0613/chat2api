from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any

from apps.user.models import User
from apps.user.utils import get_password_hash, verify_password

class UserOperation:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, name: str, email: str, password: str, role: str = "user") -> User:
        # Check if user already exists
        existing_user = UserOperation.get_user_by_email(db, email)
        if existing_user:
            raise IntegrityError("User with this email already exists", None, None)
        
        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role,
            active=True,
            created_at=datetime.now(UTC),
            last_active=datetime.now(UTC)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserOperation.get_user_by_email(db, email)
        if not user or not verify_password(password, user.password):
            return None
        
        # Update last active
        user.last_active = datetime.now(UTC)
        db.commit()
        
        return user
    
    @staticmethod
    def update_user_last_active_by_id(db: Session, user_id: int) -> bool:
        user = UserOperation.get_user_by_id(db, user_id)
        if user:
            user.last_active = datetime.now(UTC)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        user = UserOperation.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields
        for key, value in user_data.items():
            if key == 'password' and value:
                value = get_password_hash(value)
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.last_active = datetime.now(UTC)
        db.commit()
        db.refresh(user)
        return user
