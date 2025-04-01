import hashlib
import random
import time

from fastapi import HTTPException

from utils.Client import Client
from utils.Logger import logger
from utils.configs import proxy_url_list
from utils.database import get_db_context
from apps.token.operations import mark_token_as_error
from apps.token.models import Token


async def rt2ac(refresh_token, force_refresh=False):
    # 檢查資料庫中的 token 記錄
    with get_db_context() as db:
        token_record = db.query(Token).filter(Token.token == refresh_token, Token.is_refresh_token == True).first()
        
        # 如果沒有找到對應的 token 記錄，或者被標記為錯誤，拒絕處理
        if not token_record:
            logger.error(f"refresh_token not found in database")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        if token_record.is_error:
            logger.error(f"refresh_token is marked as error")
            raise HTTPException(status_code=401, detail="Refresh token is marked as error")
        
        # 檢查 token 是否在有效期內（5天），如果在有效期內且非強制刷新，直接返回現有 access_token
        current_time = int(time.time())
        refresh_threshold = 5 * 24 * 60 * 60  # 5天
        
        # 如果有關聯的 access_token 且未過期，直接返回
        access_token_record = db.query(Token).filter(
            Token.description == f"Generated from refresh token ID: {token_record.id}",
            Token.is_refresh_token == False,
            Token.is_error == False
        ).first()
        
        if not force_refresh and access_token_record and access_token_record.timestamp > 0 and (current_time - access_token_record.timestamp < refresh_threshold):
            logger.info(f"refresh_token -> access_token from database cache")
            return access_token_record.token
    
    # 需要刷新 token
    try:
        access_token = await chat_refresh(refresh_token)

        with get_db_context() as db:
            # 更新 refresh_token 的時間戳
            token_record = db.query(Token).filter(Token.token == refresh_token).first()
            if token_record:
                token_record.timestamp = int(time.time())
            
            # 尋找對應的 access_token 記錄
            access_token_record = db.query(Token).filter(
                Token.description == f"Generated from refresh token ID: {token_record.id}",
                Token.is_refresh_token == False
            ).first()
            
            # 如果已有記錄，更新它
            if access_token_record:
                access_token_record.token = access_token
                access_token_record.timestamp = int(time.time())
                access_token_record.is_error = False
            else:
                # 創建新記錄
                new_token = Token(
                    token=access_token,
                    is_refresh_token=False,
                    timestamp=int(time.time()),
                    created_by=token_record.created_by if token_record else None,
                    description=f"Generated from refresh token ID: {token_record.id}"
                )
                db.add(new_token)
            
            db.commit()
        
        logger.info(f"refresh_token -> access_token with openai: {access_token[:10]}...")
        return access_token
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


async def chat_refresh(refresh_token):
    data = {
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "grant_type": "refresh_token",
        "redirect_uri": "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback",
        "refresh_token": refresh_token
    }
    session_id = hashlib.md5(refresh_token.encode()).hexdigest()
    proxy_url = random.choice(proxy_url_list).replace("{}", session_id) if proxy_url_list else None
    client = Client(proxy=proxy_url)
    try:
        r = await client.post("https://auth0.openai.com/oauth/token", json=data, timeout=15)
        if r.status_code == 200:
            access_token = r.json()['access_token']
            return access_token
        else:
            if "invalid_grant" in r.text or "access_denied" in r.text:
                # 將 refresh_token 標記為錯誤
                with get_db_context() as db:
                    mark_token_as_error(db, refresh_token)
                raise Exception(r.text)
            else:
                raise Exception(r.text[:300])
    except Exception as e:
        logger.error(f"Failed to refresh access_token `{refresh_token}`: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh access_token.")
    finally:
        await client.close()
        del client
