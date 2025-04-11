from fastapi import APIRouter, Request, HTTPException, Cookie, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from apps.token.operations import get_all_tokens, get_all_error_tokens
from apps.user.utils import decode_token
from apps.user.operations import UserOperation
from utils.configs import api_prefix
from utils.database import get_db
from starlette.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/tokens")
async def tokens_page(
    request: Request,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """token 管理頁面 - 只有 admin 可以訪問"""
    # 驗證用戶身份
    if not jwt:
        return RedirectResponse(url="/login?redirect_url=/tokens", status_code=302)
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("jwt")
        response.delete_cookie("token")
        return response
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("jwt")
        response.delete_cookie("token")
        return response
    
    # 檢查用戶角色 - 只有 admin 可以訪問
    if user.role != "admin":
        return RedirectResponse(url="/403", status_code=302)
    
    # 獲取 token 列表
    tokens = get_all_tokens(db)
    error_tokens = get_all_error_tokens(db)
    
    return templates.TemplateResponse(
        "tokens.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "tokens_count": len(tokens),
            "error_tokens_count": len(error_tokens),
            "user": user
        }
    )


@router.get("/token_error")
async def token_error_page(
    request: Request,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """token 錯誤頁面"""
    user = None
    if jwt:
        decoded = decode_token(jwt)
        if decoded and "id" in decoded:
            user = UserOperation.get_user_by_id(db, decoded["id"])
    
    return templates.TemplateResponse(
        "token_error.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user
        }
    )
