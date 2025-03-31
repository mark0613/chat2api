from fastapi import APIRouter, Depends, HTTPException, Form, Request, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from apps.token.operations import (
    get_all_tokens,
    get_all_error_tokens,
    add_token,
    mark_token_as_error,
    delete_token,
    clear_all_tokens
)
from apps.user.utils import decode_token
from apps.user.operations import UserOperation
from utils.database import get_db
from utils.Logger import logger

router = APIRouter(prefix="/token", tags=["token"])


@router.get("/list")
def list_tokens(
    request: Request,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """獲取所有 token 列表"""
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 確保用戶有權限查看 token 列表
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # 任何已驗證的用戶都可以查看 token 列表
    tokens = get_all_tokens(db)
    error_tokens = get_all_error_tokens(db)
    
    return {
        "tokens": [{"id": t.id, "token": t.token, "description": t.description, "created_at": t.created_at} for t in tokens],
        "error_tokens": [{"id": t.id, "token": t.token, "description": t.description, "created_at": t.created_at} for t in error_tokens],
    }


@router.post("/add")
def add_new_token(
    request: Request,
    token: str = Form(...),
    description: str = Form(...),
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """添加新的 token"""
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
    
    if not token or not description:
        raise HTTPException(status_code=400, detail="Token and description cannot be empty")
    
    try:
        add_token(db, token, description, user.id)
        return {"status": "success", "message": "Token added successfully"}
    except Exception as e:
        logger.error(f"Error adding token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding token: {str(e)}")


@router.post("/delete/{token_id}")
def remove_token(
    request: Request,
    token_id: int,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """刪除指定的 token"""
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 確保用戶有權限刪除 token
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        success = delete_token(db, token_id)
        if not success:
            raise HTTPException(status_code=404, detail="Token not found")
                
        return {"status": "success", "message": "Token deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting token: {str(e)}")


@router.post("/clear")
def clear_tokens(
    request: Request,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """清空所有 token"""
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
    
    try:
        clear_all_tokens(db)
        return {"status": "success", "message": "All tokens cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing tokens: {str(e)}")


@router.post("/mark-error/{token_id}")
def mark_token_error(
    request: Request,
    token_id: int,
    jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """將指定 token 標記為錯誤"""
    # 驗證用戶身份
    if not jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    decoded = decode_token(jwt)
    if not decoded or "id" not in decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserOperation.get_user_by_id(db, decoded["id"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 確保用戶有權限標記 token 為錯誤
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    token = None
    for t in get_all_tokens(db):
        if t.id == token_id:
            token = t
            break
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    try:
        mark_token_as_error(db, token.token)
        return {"status": "success", "message": "Token marked as error successfully"}
    except Exception as e:
        logger.error(f"Error marking token as error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking token as error: {str(e)}")
