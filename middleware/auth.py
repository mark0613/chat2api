import urllib.parse
import logging
from typing import Optional, List, Dict, Any
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from contextlib import contextmanager

from apps.user.utils import decode_token
from apps.user.models import User
from utils.database import get_db

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # 不需要驗證的路徑
        self.excluded_paths = [
            "/login", "/register", "/user/login", "/user/register", "/logout",
            "/static", "/favicon.ico", "/api", "/docs", "/redoc", "/token_error", "/403",
            "/v1", "/admin/api"
        ]
        # 需要檢查 token 的路徑
        self.token_required_paths = [
            "/", "/c/", "/settings", "/profile", "/admin"
        ]

    async def dispatch(self, request: Request, call_next):
        jwt = request.cookies.get("jwt")
        path = request.url.path
        
        # 初始化 request.state.user 為 None
        request.state.user = None
        
        # 1. 獲取並存儲使用者
        if jwt and self._is_valid_jwt(jwt):
            try:
                user = self._get_user_from_jwt(jwt)
                if user:
                    request.state.user = user
                    
                # 如果用戶已登入且嘗試訪問登入或註冊頁面，重定向到首頁
                if path == "/login" or path == "/register":
                    return RedirectResponse(url="/", status_code=302)
            except Exception as e:
                logger.error(f"獲取使用者時發生錯誤: {str(e)}")
        
        # 2. 檢查路徑是否需要跳過驗證
        skip_auth = False
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                skip_auth = True
                break
        
        # 3. 檢查是否需要認證
        if not skip_auth:
            for token_path in self.token_required_paths:
                if path.startswith(token_path):
                    if not request.state.user:
                        if not jwt:
                            current_url = str(request.url)
                            encoded_url = urllib.parse.quote(current_url)
                            return RedirectResponse(
                                url=f"/login?redirect_url={encoded_url}", 
                                status_code=302
                            )
                        else:
                            response = RedirectResponse(url="/login", status_code=302)
                            response.delete_cookie("jwt")
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
        
    def _get_user_from_jwt(self, jwt: str):
        decoded = decode_token(jwt)
        if decoded and "id" in decoded:
            with next(get_db()) as db:
                return db.query(User).filter(User.id == decoded["id"]).first()
        return None
