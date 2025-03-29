import json
import urllib.parse
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr

from utils.database import get_db
from apps.user.utils import create_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from apps.user.operations import UserOperation
from apps.user.models import User
from chatgpt.authorization import get_token

router = APIRouter(tags=["user"], prefix="/user")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str
    email: str
    role: str

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True

# API Routes
@router.post("/register", response_model=Token)
async def register_api(user_data: UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        user = UserOperation.create_user(
            db=db,
            name=user_data.name, 
            email=user_data.email, 
            password=user_data.password
        )
        
        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_token(
            data={"id": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Set cookie
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_api(user_data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    user = UserOperation.authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"id": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Set cookie
    response.set_cookie(
        key="jwt",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )

    token = get_token()
    if token:
        tomorrow = datetime.now() + timedelta(days=1)
        expires = tomorrow.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response.set_cookie("token", value=get_token(), expires=expires)
    
    # 建立回應資料
    result = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    redirect_url = request.query_params.get("redirect_url")
    if redirect_url:
        result["redirect_url"] = redirect_url
    return result

@router.post("/logout")
async def logout_api(response: Response):
    response.delete_cookie(key="token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
