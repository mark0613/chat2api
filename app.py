import warnings

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from middleware.auth import AuthMiddleware
from middleware.token import TokenCheckMiddleware
from middleware.role import RoleMiddleware
from utils.configs import enable_gateway, api_prefix
from utils.database import init_db

warnings.filterwarnings("ignore")

log_config = uvicorn.config.LOGGING_CONFIG
default_format = "%(asctime)s | %(levelname)s | %(message)s"
access_format = r'%(asctime)s | %(levelname)s | %(client_addr)s: %(request_line)s %(status_code)s'
log_config["formatters"]["default"]["fmt"] = default_format
log_config["formatters"]["access"]["fmt"] = access_format

app = FastAPI(
    docs_url=f"/{api_prefix}/docs" if api_prefix else "/docs",    # 設置 Swagger UI 文檔路徑
    redoc_url=f"/{api_prefix}/redoc" if api_prefix else "/redoc",  # 設置 Redoc 文檔路徑
    openapi_url=f"/{api_prefix}/openapi.json" if api_prefix else "/openapi.json"  # 設置 OpenAPI JSON 路徑
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
security_scheme = HTTPBearer()


@app.on_event("startup")
async def startup_event():
    init_db()

from app import app

import api.chat2api

if enable_gateway:
    from apps.user import routes as user_routes
    from apps.user import views as user_views
    from apps.user import admin_routes as user_admin_routes
    from apps.user import admin_views as user_admin_views
    from apps.token import routes as token_routes
    from apps.token import views as token_views

    # 中間件添加的順序與執行順序相反 - 後添加的先執行
    app.add_middleware(TokenCheckMiddleware)
    app.add_middleware(RoleMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # API
    app.include_router(user_routes.router, prefix="/api")
    app.include_router(token_routes.router, prefix="/api")
    app.include_router(user_admin_routes.router, prefix="/api")

    # Views
    app.include_router(user_views.router)
    app.include_router(token_views.router)
    app.include_router(user_admin_views.router)
    
    import gateway.share
    import gateway.chatgpt
    import gateway.gpts
    import gateway.admin
    import gateway.v1
    import gateway.backend
else:
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
    async def reverse_proxy():
        raise HTTPException(status_code=404, detail="Gateway is disabled")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5005)
    # uvicorn.run("app:app", host="0.0.0.0", port=5005, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
