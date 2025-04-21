from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from apps.token.operations import (
    add_token,
    clear_all_tokens,
    delete_token,
    get_all_error_tokens,
    get_all_tokens,
    update_token_status as update_token_status_operation,
    get_token_by_id,
)
from utils.database import get_db
from utils.Logger import logger

router = APIRouter(prefix='/token', tags=['token'])


@router.get('/list')
def list_tokens(
    request: Request,
    db: Session = Depends(get_db),
):
    # 獲取 token 列表
    tokens = get_all_tokens(db)
    error_tokens = get_all_error_tokens(db)

    return {
        'tokens': [
            {
                'id': t.id,
                'token': t.token,
                'description': t.description,
                'created_at': t.created_at,
            }
            for t in tokens
        ],
        'error_tokens': [
            {
                'id': t.id,
                'token': t.token,
                'description': t.description,
                'created_at': t.created_at,
            }
            for t in error_tokens
        ],
    }


@router.post('/add')
def add_new_token(
    request: Request,
    token: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    """添加新的 token"""
    user = getattr(request.state, 'user', None)

    if not token or not description:
        raise HTTPException(status_code=400, detail='Token and description cannot be empty')

    try:
        _, error_message = add_token(db, token, description, user.id)
        if error_message:
            if '已存在' in error_message:
                raise HTTPException(status_code=409, detail=error_message)
            raise HTTPException(status_code=500, detail=error_message)

        return {'status': 'success', 'message': 'Token added successfully'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error adding token: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error adding token: {str(e)}')


@router.post('/delete/{token_id}')
def remove_token(request: Request, token_id: int, db: Session = Depends(get_db)):
    """刪除指定的 token"""

    try:
        success = delete_token(db, token_id)
        if not success:
            raise HTTPException(status_code=404, detail='Token not found')

        return {'status': 'success', 'message': 'Token deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error deleting token: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error deleting token: {str(e)}')


@router.post('/clear')
def clear_tokens(request: Request, db: Session = Depends(get_db)):
    """清空所有 token"""

    try:
        clear_all_tokens(db)
        return {'status': 'success', 'message': 'All tokens cleared successfully'}
    except Exception as e:
        logger.error(f'Error clearing tokens: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error clearing tokens: {str(e)}')


@router.post('/update-status/{token_id}')
def update_token_status(
    request: Request,
    token_id: int,
    is_error: bool = Form(...),
    db: Session = Depends(get_db),
):
    """更新指定 token 的狀態"""
    token = get_token_by_id(db, token_id)
    try:
        update_token_status_operation(db, is_error, token=token)
        return {'status': 'success', 'message': 'Token status updated successfully'}
    except Exception as e:
        logger.error(f'Error updating token status: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error updating token status: {str(e)}')
   
