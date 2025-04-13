from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from apps.user.utils import decode_token
from app import templates
from utils.configs import api_prefix

router = APIRouter(tags=["user_views"])

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, redirect_url: Optional[str] = Query(None)):
    return templates.TemplateResponse(
        "login_register.html", 
        {"request": request, "redirect_url": redirect_url}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, redirect_url: Optional[str] = Query(None)):
    return templates.TemplateResponse(
        "login_register.html", 
        {"request": request, "active_tab": "register", "redirect_url": redirect_url}
    )

@router.get("/logout")
async def logout_redirect():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="jwt")
    response.delete_cookie(key="token")
    return response

@router.get("/403")
async def forbidden_page(request: Request):
    return templates.TemplateResponse(
        "403.html",
        {
            "request": request,
            "api_prefix": api_prefix
        }
    )

@router.get("/waiting", response_class=HTMLResponse)
async def waiting_page(request: Request):
    return templates.TemplateResponse("waiting.html", {"request": request})
