from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from apps.user.models import User
from utils.configs import api_prefix

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.get('/token_error')
async def token_error_page(request: Request):
    """token 錯誤頁面"""
    user: User = request.state.user
    return templates.TemplateResponse(
        'token_error.html', {'request': request, 'api_prefix': api_prefix, 'user': user}
    )
