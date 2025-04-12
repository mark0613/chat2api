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
