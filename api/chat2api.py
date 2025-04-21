import asyncio
import types
from functools import wraps
from uuid import uuid4

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
from utils.configs import api_prefix, scheduled_refresh, authorization_list, pipeline_enable
from utils.retry import async_retry
from utils.database import get_db, get_db_context
from apps.token.operations import mark_token_as_error, get_available_token
from apps.user.utils import decode_token
from apps.user.operations import UserOperation
from apps.pipeline import process_pipeline_inlet_filter, process_pipeline_outlet_filter

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


def convert_official_to_pipeline_output(input: dict, output: dict):
    messages: list = input.get("messages", [])
    messages.append({
        "role": output['choices'][0]['message']['role'],
        "content": output['choices'][0]['message']['content'],
    })

    metadata = input.get("metadata", {})

    return {
        "model": input['model'],
        "messages": messages,
        "chat_id": metadata["chat_id"],
        "source_output": output,
    }

def convert_pipeline_to_official_output(data: dict):
    return data["source_output"]

def process_with_pipeline(func):
    @wraps(func)
    async def wrapper(request_data, req_token, user=None):
        chat_id = str(uuid4())
        request_data["metadata"] = {
            "chat_id": chat_id,
        }

        # pipeline inlet
        if pipeline_enable:
            try:
                user_info = {"id": user.id, "name": user.name, "email": user.email, "role": user.role} if user else {}
                request_data = await process_pipeline_inlet_filter(request_data, user_info)
            except Exception as e:
                logger.error(f"Error processing pipeline inlet filter: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

        # process
        chat_service, res = await func(request_data, req_token, user=None)

        # pipeline outlet
        if pipeline_enable:
            try:
                user_info = {"id": user.id, "name": user.name, "email": user.email, "role": user.role} if user else {}
                res = convert_official_to_pipeline_output(request_data, res)
                res = await process_pipeline_outlet_filter(res, user_info)
                res = convert_pipeline_to_official_output(res)
            except Exception as e:
                logger.error(f"Error processing pipeline outlet filter: {str(e)}")
        return chat_service, res

    return wrapper

@process_with_pipeline
async def process(request_data, req_token, user=None):
    chat_service = await to_send_conversation(request_data, req_token)
    await chat_service.prepare_send_conversation()
    res = await chat_service.send_conversation()
    return chat_service, res


@app.post(f"/{api_prefix}/v1/chat/completions" if api_prefix else "/v1/chat/completions")
async def send_conversation(request: Request, credentials: HTTPAuthorizationCredentials = Security(security_scheme), db: Session = Depends(get_db)):
    # 獲取請求中的 token（必須提供）
    req_token = credentials.credentials
    
    # TODO: 目前先固定，未來每個 user 都有自己的 api-keys
    user = UserOperation.get_first_user(db)

    try:
        request_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Invalid JSON body"})
    
    chat_service, res = await async_retry(process, request_data, req_token, user)
    
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


@app.get(f"/{api_prefix}/v1/models" if api_prefix else "/v1/models")
async def get_models(request: Request, credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    req_token = credentials.credentials
    
    if req_token not in authorization_list:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")

    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai"
            },
            {
                "id": "o3-mini",
                "object": "model",
                "created": 1737146383,
                "owned_by": "system"
            },
            {
                "id": "o3-mini-high",
                "object": "model",
                "created": 1737146383,
                "owned_by": "system"
            },
            {
                "id": "o1",
                "object": "model",
                "created": 1734375816,
                "owned_by": "system"
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": 1715367049,
                "owned_by": "system"
            },
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": 1721172741,
                "owned_by": "system"
            }
        ]
    }
