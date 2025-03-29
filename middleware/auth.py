import urllib.parse
from typing import Optional, List, Dict, Any

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from apps.user.utils import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # 不需要驗證的路徑
        self.excluded_paths = [
            "/login", "/register", "/user/login", "/user/register", "/logout",
            "/static", "/favicon.ico", "/api", "/docs", "/redoc", "/token_error"
        ]
        # 需要檢查 token 的路徑
        self.token_required_paths = [
            "/", "/c/", "/settings", "/profile"
        ]

    async def dispatch(self, request: Request, call_next):
        jwt = request.cookies.get("jwt")
        token = request.cookies.get("token")
        path = request.url.path
        
        # 1. 已登入用戶訪問登入/註冊頁面的情況
        if jwt and token and self._is_valid_jwt(jwt):
            # 如果用戶已登入且嘗試訪問登入或註冊頁面，重定向到首頁
            if path == "/login" or path == "/register":
                return RedirectResponse(url="/", status_code=302)
        
        # 2. 檢查路徑是否需要跳過驗證
        skip_auth = False
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                skip_auth = True
                break
        
        # 3. 檢查 JWT 和 token
        if not skip_auth:
            if not jwt or not token or not self._is_valid_jwt(jwt):
                for token_path in self.token_required_paths:
                    if path.startswith(token_path):
                        if not jwt:
                            current_url = str(request.url)
                            encoded_url = urllib.parse.quote(current_url)
                            return RedirectResponse(
                                url=f"/login?redirect_url={encoded_url}", 
                                status_code=302
                            )
                        elif jwt and not self._is_valid_jwt(jwt):
                            response = RedirectResponse(url="/login", status_code=302)
                            response.delete_cookie("jwt")
                            response.delete_cookie("token")
                            return response
                        break
        
        # 繼續處理請求
        response = await call_next(request)
        return response
    
    def _is_valid_jwt(self, jwt: str) -> bool:
        decoded = decode_token(jwt)
        if decoded and "id" in decoded:
            return True
        return False
