from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from apps.token.operations import get_all_tokens, get_all_error_tokens
from apps.user.utils import get_current_user_from_cookie
from apps.user.models import User
from utils.database import get_db
from utils.configs import api_prefix
from app import templates

router = APIRouter(tags=["admin_views"])

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "admin_dashboard.html", 
        {
            "request": request, 
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "dashboard" 
        }
    )

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "admin_dashboard.html", 
        {
            "request": request, 
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "users"
        }
    )

@router.get("/admin/tokens", response_class=HTMLResponse)
async def admin_tokens(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    tokens = get_all_tokens(db)
    error_tokens = get_all_error_tokens(db)
    
    return templates.TemplateResponse(
        "admin_dashboard.html", 
        {
            "request": request, 
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "tokens",
            "tokens_count": len(tokens),
            "error_tokens_count": len(error_tokens)
        }
    )
