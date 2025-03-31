import time

from utils.Logger import logger
from utils.database import get_db_context
from apps.token.models import Token
from apps.token.operations import update_token_timestamp


def update_wss_info(token_value, wss_mode, wss_url=None):
    """更新 token 的 WebSocket 相關信息
    
    將 WSS 相關信息存儲在 token 的 description 中，格式為 JSON
    """
    with get_db_context() as db:
        token = db.query(Token).filter(Token.token == token_value).first()
        if token:
            token.timestamp = int(time.time())
            original_desc = token.description
            token.description = f"{original_desc} [WSS:{wss_mode}:{wss_url if wss_url else 'None'}]"
            
            db.commit()
            return True
    return False


async def token2wss(token_value, threshold=60*60):
    """根據 token 獲取 WebSocket 訊息
    
    Args:
        token_value: token 值
        threshold: 過期門檯ff08秒），預設 1 小時
        
    Returns:
        (wss_mode, wss_url): 元組，包含 WebSocket 模式和 URL
    """
    if not token_value:
        return False, None
    
    with get_db_context() as db:
        token = db.query(Token).filter(Token.token == token_value).first()
        if not token:
            return False, None
        
        # 如果 token 已經有時間戳且未過期
        current_time = int(time.time())
        if token.timestamp > 0 and (current_time - token.timestamp < threshold):
            # 從 description 中提取 WSS 信息
            if "[WSS:" in token.description:
                wss_info = token.description.split("[WSS:")[1].split("]")[0]
                wss_parts = wss_info.split(":")
                
                wss_mode = wss_parts[0] == "True"
                wss_url = None if wss_parts[1] == "None" else wss_parts[1]
                
                logger.info(f"token -> wss_url from database cache")
                return wss_mode, wss_url
    
    # 如果沒有找到或過期
    logger.info(f"token -> wss_url not found or expired")
    return False, None


async def set_wss(token_value, wss_mode, wss_url=None):
    """設定 token 的 WebSocket 訊息"""
    if not token_value:
        return True
    
    success = update_wss_info(token_value, wss_mode, wss_url)
    return success
