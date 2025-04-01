import asyncio
import types

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Request, HTTPException, Form, Security, Depends, Cookie, Header
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session
from typing import Optional

from app import app, templates, security_scheme
from chatgpt.ChatService import ChatService
from chatgpt.authorization import refresh_all_tokens
from utils.Logger import logger
from utils.configs import api_prefix, scheduled_refresh
from utils.retry import async_retry
from utils.database import get_db, get_db_context
from apps.token.operations import mark_token_as_error, get_all_tokens, get_all_error_tokens, add_token, clear_all_tokens, get_available_token
from apps.user.utils import decode_token
from apps.user.operations import UserOperation

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def app_start():
    if scheduled_refresh:
        scheduler.add_job(id='refresh', func=refresh_all_tokens, trigger='cron', hour=3, minute=0, day='*/2',
                          kwargs={'force_refresh': True})
        scheduler.start()
        asyncio.get_event_loop().call_later(0, lambda: asyncio.create_task(refresh_all_tokens(force_refresh=False)))


def get_api_token(db: Session):
    token = get_available_token(db, threshold=60*60, prefer_access_token=True)
    if not token:
        raise HTTPException(status_code=503, detail="No available tokens")
    return token


async def to_send_conversation(request_data, req_token):
    # 必須提供 token
    if not req_token:
        raise HTTPException(status_code=401, detail="Unauthorized: No token provided")
    
    chat_service = ChatService(req_token)
    try:
        await chat_service.set_dynamic_data(request_data)
        await chat_service.get_chat_requirements()
        return chat_service
    except HTTPException as e:
        await chat_service.close_client()
        # 如果 token 出錯，將其標記為錯誤
        if e.status_code in [401, 403, 429] and req_token:
            with get_db_context() as db:
                mark_token_as_error(db, req_token)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        await chat_service.close_client()
        logger.error(f"Server error, {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


async def process(request_data, req_token):
    chat_service = await to_send_conversation(request_data, req_token)
    await chat_service.prepare_send_conversation()
    res = await chat_service.send_conversation()
    return chat_service, res


@app.post(f"/{api_prefix}/v1/chat/completions" if api_prefix else "/v1/chat/completions")
async def send_conversation(request: Request, credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    # 獲取請求中的 token（必須提供）
    req_token = credentials.credentials
    
    try:
        request_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Invalid JSON body"})
    
    chat_service, res = await async_retry(process, request_data, req_token)
    
    try:
        if isinstance(res, types.AsyncGeneratorType):
            background = BackgroundTask(chat_service.close_client)
            return StreamingResponse(res, media_type="text/event-stream", background=background)
        else:
            background = BackgroundTask(chat_service.close_client)
            return JSONResponse(res, media_type="application/json", background=background)
    except HTTPException as e:
        await chat_service.close_client()
        if e.status_code == 500:
            logger.error(f"Server error, {str(e)}")
            raise HTTPException(status_code=500, detail="Server error")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        await chat_service.close_client()
        logger.error(f"Server error, {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


# 舊的 API 接口，保留以支持向下兼容
@app.get(f"/{api_prefix}/tokens" if api_prefix else "/tokens", response_class=HTMLResponse)
async def upload_html(request: Request):
    # 重定向到新的 tokens 管理頁面
    return RedirectResponse(url="/tokens", status_code=302)


@app.post(f"/{api_prefix}/tokens/upload" if api_prefix else "/tokens/upload")
async def upload_post(
    text: str = Form(...),
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    lines = text.split("\n")
    for line in lines:
        if line.strip() and not line.startswith("#"):
            add_token(db, line.strip(), "Added via bulk upload", user.id)
    
    tokens_count = len(get_all_tokens(db))
    return {"status": "success", "tokens_count": tokens_count}


@app.post(f"/{api_prefix}/tokens/clear" if api_prefix else "/tokens/clear")
async def clear_tokens_api(
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 確保用戶有權限清空 tokens
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    clear_all_tokens(db)
    return {"status": "success", "tokens_count": 0}


@app.post(f"/{api_prefix}/tokens/error" if api_prefix else "/tokens/error")
async def error_tokens_api(
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    error_tokens = get_all_error_tokens(db)
    return {"status": "success", "error_tokens": [t.token for t in error_tokens]}


@app.get(f"/{api_prefix}/tokens/add/{{token}}" if api_prefix else "/tokens/add/{token}")
async def add_token_api(
    token: str,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 確保用戶有權限添加 token
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if token.strip() and not token.startswith("#"):
        add_token(db, token.strip(), "Added via API", user.id)
    
    tokens_count = len(get_all_tokens(db))
    return {"status": "success", "tokens_count": tokens_count}


@app.post(f"/{api_prefix}/seed_tokens/clear" if api_prefix else "/seed_tokens/clear")
async def clear_seed_tokens():
    # 不再使用 globals 變量和文件存儲 seed tokens
    # 此函數保留以向後兼容，但不再執行實際操作
    logger.info("seed_tokens/clear API called but functionality has been replaced with database storage")
    return {"status": "success", "seed_tokens_count": 0}
