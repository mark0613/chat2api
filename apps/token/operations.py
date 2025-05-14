import time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.token.models import Token
from utils.Logger import logger


def check_token_type(token_value: str):
    """檢查 token 類型

    返回值:
        (is_access_token, is_refresh_token): (bool, bool) 元組，表示 token 的類型
    """
    # 檢查是否為 access_token (以 eyJhbGciOi 開頭或 fk- 開頭)
    if token_value.startswith('eyJhbGciOi') or token_value.startswith('fk-'):
        return True, False

    # 檢查是否為 refresh_token (長度為 45 字符)
    elif len(token_value) == 45:
        return False, True

    # 既不是 access_token 也不是 refresh_token
    return False, False

def get_token_by_id(db: Session, token_id: int):
    return db.query(Token).filter(Token.id == token_id).first()


def get_all_tokens(db: Session):
    """取得所有未處於錯誤狀態的 token"""
    return db.query(Token).filter(Token.is_error == False).all()


def get_all_error_tokens(db: Session):
    """取得所有處於錯誤狀態的 token"""
    return db.query(Token).filter(Token.is_error == True).all()


def add_token(db: Session, token_value: str, description: str, user_id: int):
    """添加一個新的 token，並自動檢查其類型"""
    existing_token = db.query(Token).filter(Token.token == token_value).first()
    if existing_token:
        logger.warning(f'Attempted to add duplicate token: {token_value[:5]}...')
        return None, 'Token 已存在，無法重複添加'

    is_access_token, is_refresh_token = check_token_type(token_value)

    # 創建 token 記錄
    token = Token(
        token=token_value,
        description=description,
        created_by=user_id,
        is_refresh_token=is_refresh_token,
        is_error=not (is_access_token or is_refresh_token),
    )

    try:
        db.add(token)
        db.commit()

        if not (is_access_token or is_refresh_token):
            logger.warning(f'Added invalid token marked as error: {token_value[:5]}...')
        else:
            token_type = 'refresh_token' if is_refresh_token else 'access_token'
            logger.info(f'Added new {token_type} with description: {description}')

        return token, None
    except IntegrityError:
        db.rollback()
        return None, 'Token 已存在，無法重複添加'
    except Exception as e:
        db.rollback()
        logger.error(f'Error adding token: {str(e)}')
        return None, f'添加 Token 時發生錯誤: {str(e)}'


def update_token_status(db: Session, is_error: bool, token_value: str = "", token: Token = None):
    """更新指定 token 的狀態"""
    if not token:
        token = db.query(Token).filter(Token.token == token_value).first()
    if token:
        token.is_error = is_error
        db.commit()
        logger.info(f'Updated token {token_value[:5]}... status to {"error" if is_error else "valid"}')
        return True
    return False


def mark_token_as_error(db: Session, token_value: str):
    """將指定的 token 標記為錯誤狀態"""
    return update_token_status(db, token_value=token_value, is_error=True)


def mark_token_as_valid(db: Session, token_value: str):
    """將指定的 token 標記為有效狀態"""
    return update_token_status(db, token_value=token_value, is_error=False)

def delete_token(db: Session, token_id: int):
    """刪除指定的 token"""
    token = db.query(Token).filter(Token.id == token_id).first()
    if token:
        db.delete(token)
        db.commit()
        logger.info(f'Deleted token with id: {token_id}')
        return True
    return False


def clear_all_tokens(db: Session):
    """清空所有 token"""
    db.query(Token).delete()
    db.commit()
    logger.info('Cleared all tokens')
    return True


def fix_latest_token_error(db: Session):
    """找到最新創建的 token 並將其 is_error 狀態設為 False"""
    latest_token = db.query(Token).order_by(Token.created_at.desc()).first()
    if latest_token:
        latest_token.is_error = False
        db.commit()
        logger.info(f'Fixed error status for latest token with id: {latest_token.id}')
        return True, None
    else:
        return False, "No tokens found to fix."

def has_active_tokens(db: Session):
    """檢查是否有可用的 token"""
    return db.query(Token).filter(Token.is_error == False).first() is not None


def get_available_token(db: Session, threshold: int = 60 * 60, prefer_access_token: bool = True):
    """
    獲取一個可用的 token

    Args:
        db: 數據庫會話
        threshold: 過期閾值（秒），默認1小時
        prefer_access_token: 是否優先選擇 access_token，默認為 True

    Returns:
        可用的 token 字符串或 None
    """
    # 一次性獲取所有非錯誤的 token
    tokens = db.query(Token).filter(Token.is_error == False).all()

    if not tokens:
        return None

    current_time = int(time.time())
    available_access_tokens = []
    available_refresh_tokens = []

    # 分類 token
    for token in tokens:
        # 超過閾值的 token 標記為錯誤（只檢查有時間戳的 token）
        if token.timestamp > 0 and (current_time - token.timestamp > threshold):
            token.is_error = True
            logger.warning(f'Token {token.token[:5]}... marked as error due to timeout')
            continue

        if token.is_refresh_token:
            available_refresh_tokens.append(token)
        else:
            available_access_tokens.append(token)

    # 在標記完錯誤後提交更改
    if tokens and not (available_access_tokens or available_refresh_tokens):
        db.commit()

    # 按照優先順序選擇 token
    if prefer_access_token:
        if available_access_tokens:
            return available_access_tokens[0].token
        elif available_refresh_tokens:
            return available_refresh_tokens[0].token
    else:
        if available_refresh_tokens:
            return available_refresh_tokens[0].token
        elif available_access_tokens:
            return available_access_tokens[0].token

    return None
