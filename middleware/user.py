from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import time
import logging

from utils.database import get_db_context
from apps.user.utils import decode_token
from apps.user.models import User
from apps.user.operations import UserOperation

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

class UserActivityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.update_interval = 300  # 5分鐘
        self.user_last_updates = {}
    
    async def dispatch(self, request: Request, call_next):
        jwt = request.cookies.get("jwt")
        if jwt:
            try:
                await self._update_user_activity_if_needed(jwt)
            except Exception as e:
                logger.error(f"更新用戶活動時間時發生錯誤: {str(e)}")

        response = await call_next(request)
        return response
    
    async def _update_user_activity_if_needed(self, jwt: str):
        decoded = decode_token(jwt)
        if not decoded or "id" not in decoded:
            return
        
        user_id = decoded["id"]
        current_time = time.time()
        
        if user_id not in self.user_last_updates or \
           (current_time - self.user_last_updates[user_id]) > self.update_interval:

            with get_db_context() as db:
                self._update_user_last_active(db, user_id)
                db.commit()
            
            # 更新快取
            self.user_last_updates[user_id] = current_time
    
    @staticmethod
    def _update_user_last_active(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_active = datetime.now(timezone.utc)


class UserActiveCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.whitelist_paths = [
            "/login", 
            "/register", 
            "/logout", 
            "/waiting", 
            "/api/login", 
            "/api/register",
            "/api/logout",
            "/static/",
            "/favicon.ico",
            "/v1",
        ]
    
    async def dispatch(self, request: Request, call_next):
        for path in self.whitelist_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        jwt = request.cookies.get("jwt")
        decoded = decode_token(jwt)
        if not decoded or "id" not in decoded:
            return await call_next(request)
        user_id = decoded["id"]

        with get_db_context() as db:
            user = UserOperation.get_user_by_id(db, user_id)
            if user and not user.active:
                html_content = templates.TemplateResponse("waiting.html", {"request": request})
                return HTMLResponse(content=html_content.body, status_code=200)

        return await call_next(request)
