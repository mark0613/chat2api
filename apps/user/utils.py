from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, UTC, timedelta
import jwt
from typing import Optional, Dict, Any
import os

from utils.database import get_db
from apps.user.models import User

# Environment variables or configs (could be moved to env.py)
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Setup password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security bearer for token authentication
bearer_security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) if hashed_password else False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
        payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except Exception:
        return None

def extract_token_from_auth_header(auth_header: str) -> str:
    return auth_header[len("Bearer "):]

def get_current_user(
    auth_token: HTTPAuthorizationCredentials = Depends(bearer_security),
    db: Session = Depends(get_db)
):
    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = auth_token.credentials
    data = decode_token(token)
    
    if data is None or "id" not in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == data["id"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Update last active timestamp
    user.last_active = datetime.now(UTC)
    db.commit()
    
    return user

def get_verified_user(user: User = Depends(get_current_user)):
    if user.role not in {"user", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access prohibited"
        )
    return user

def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access prohibited"
        )
    return user

def get_current_user_from_cookie(
    request: Request,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    data = decode_token(jwt)
    
    if data is None or "id" not in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == data["id"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user
