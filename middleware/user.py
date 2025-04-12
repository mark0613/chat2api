from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import time
import logging

from utils.database import get_db_context
from apps.user.utils import decode_token
from apps.user.models import User

logger = logging.getLogger(__name__)

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
