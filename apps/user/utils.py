import os
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

# Environment variables or configs (could be moved to env.py)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Setup password context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

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
        payload.update({'exp': expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except Exception:
        return None
