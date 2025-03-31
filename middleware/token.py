from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from utils.database import get_db
from apps.token.operations import has_active_tokens


class TokenCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # 不需要檢查 token 的路徑
        self.excluded_paths = [
            "/login", "/register", "/user/login", "/user/register", "/logout",
            "/static", "/favicon.ico", "/api", "/docs", "/redoc", "/token_error", "/403",
            "/tokens", "/token/", "/user/"
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        # 檢查路徑是否需要跳過 token 檢查
        skip_check = False
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                skip_check = True
                break
        
        # 如果需要檢查 token，且不是 API 請求 (例如頁面請求)
        if not skip_check and not "/api/" in path:
            # 直接使用數據庫檢查
            with next(get_db()) as db:
                if not has_active_tokens(db):
                    return RedirectResponse(url="/token_error", status_code=302)
        
        # 繼續處理請求
        response = await call_next(request)
        return response
