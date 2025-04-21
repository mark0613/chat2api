from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from utils.configs import api_prefix
from app import templates
from apps.user.models import User

router = APIRouter(tags=["admin_views"])


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user: User = request.state.user
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "dashboard",
        },
    )


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    user: User = request.state.user
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "users",
        },
    )


@router.get("/admin/tokens", response_class=HTMLResponse)
async def admin_tokens(request: Request):
    user: User = request.state.user
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "tokens",
        },
    )


@router.get("/admin/pipelines", response_class=HTMLResponse)
async def admin_pipelines(request: Request):
    user: User = request.state.user
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "api_prefix": api_prefix,
            "user": user,
            "active_tab": "pipelines",
        },
    )
