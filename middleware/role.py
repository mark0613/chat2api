from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from utils.database import get_db
from apps.user.utils import decode_token
from apps.user.models import User

class RoleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_paths=None):
        super().__init__(app)
        # 定義受保護的路徑和對應的角色，格式為 {路徑: [角色]}
        self.protected_paths = protected_paths or {
            "/admin": ["admin"],
        }
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # 檢查是否需要角色權限
        is_protected = False
        required_roles = []
        
        for prefix, allowed_roles in self.protected_paths.items():
            if path.startswith(prefix):
                is_protected = True
                required_roles = allowed_roles
                break
        
        # 如果是受保護的路徑，檢查用戶角色
        if is_protected:
            jwt = request.cookies.get("jwt")
            if not jwt:
                return RedirectResponse(url="/login", status_code=303)

            data = decode_token(jwt)
            if not data or "id" not in data:
                return RedirectResponse(url="/403", status_code=303)

            with next(get_db()) as db:
                user = db.query(User).filter(User.id == data["id"]).first()
                if not user:
                    return RedirectResponse(url="/403", status_code=303)

                if user.role not in required_roles:
                    return RedirectResponse(url="/403", status_code=303)

        return await call_next(request)
