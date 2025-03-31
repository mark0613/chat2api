import asyncio
import time

from fastapi import HTTPException

import utils.configs as configs
from chatgpt.refreshToken import rt2ac
from utils.Logger import logger
from utils.database import get_db
from apps.token.operations import get_all_tokens, get_all_error_tokens, mark_token_as_error, get_available_token, update_token_timestamp


def get_req_token(req_token, seed=None):
    """
    獲取請求 token
    - 如果提供了 req_token，則優先使用
    - 如果沒有提供 req_token，則從數據庫獲取一個可用的 token
    """
    if req_token:
        return req_token
    
    # 從數據庫獲取可用的 token，優先選擇 access_token
    with next(get_db()) as db:
        selected_token = get_available_token(db, threshold=60*60, prefer_access_token=True)
        if not selected_token:
            return ""

        update_token_timestamp(db, selected_token)
        return selected_token
    
    
async def verify_token(req_token):
    if not req_token:
        if configs.authorization_list:
            logger.error("Unauthorized with empty token.")
            raise HTTPException(status_code=401)
        else:
            return None
    else:
        with next(get_db()) as db:
            update_token_timestamp(db, req_token)
        
        if req_token.startswith("eyJhbGciOi") or req_token.startswith("fk-"):
            access_token = req_token
            return access_token
        elif len(req_token) == 45:
            try:
                # 從數據庫檢查是否為錯誤 token
                with next(get_db()) as db:
                    error_tokens = get_all_error_tokens(db)
                    error_token_list = [t.token for t in error_tokens]
                    
                    if req_token in error_token_list:
                        raise HTTPException(status_code=401, detail="Error RefreshToken")

                access_token = await rt2ac(req_token, force_refresh=False)
                return access_token
            except HTTPException as e:
                # 如果刷新失敗，將 token 標記為錯誤
                if e.status_code in [401, 403, 429]:
                    try:
                        with next(get_db()) as db:
                            mark_token_as_error(db, req_token)
                    except Exception as mark_error:
                        logger.error(f"Failed to mark token as error: {str(mark_error)}")
                raise HTTPException(status_code=e.status_code, detail=e.detail)
        else:
            return req_token


async def refresh_all_tokens(force_refresh=False):
    # 從數據庫獲取所有 tokens
    with next(get_db()) as db:
        tokens = get_all_tokens(db)
        
        for token_obj in tokens:
            token = token_obj.token
            if len(token) == 45:
                try:
                    await asyncio.sleep(0.5)
                    await rt2ac(token, force_refresh=force_refresh)
                except HTTPException as e:
                    # 如果刷新失敗，將 token 標記為錯誤
                    if e.status_code in [401, 403, 429]:
                        try:
                            mark_token_as_error(db, token)
                            logger.error(f"Token refresh failed, marked as error: {token[:5]}...")
                        except Exception as mark_error:
                            logger.error(f"Failed to mark token as error: {str(mark_error)}")
    logger.info("All tokens refreshed.")


def get_token():
    with next(get_db()) as db:
        selected_token = get_available_token(db, threshold=60*60, prefer_access_token=True)
        if selected_token:
            update_token_timestamp(db, selected_token)
        return selected_token
