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
from apps.user.models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/token_error")
async def token_error_page(request: Request):
    """token 錯誤頁面"""
    user: User = request.state.user
    return templates.TemplateResponse(
        "token_error.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user
        }
    )
