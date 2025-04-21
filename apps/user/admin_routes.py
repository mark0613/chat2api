from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from apps.user.models import User
from apps.user.operations import UserOperation
from utils.database import get_db
from utils.Logger import logger

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/users')
def list_users(request: Request, db: Session = Depends(get_db)):
    try:
        users = UserOperation.get_all_users(db)
        return {
            'status': 'success',
            'users': [
                {
                    'id': u.id,
                    'name': u.name,
                    'email': u.email,
                    'active': u.active,
                    'role': u.role,
                    'created_at': u.created_at.isoformat() if u.created_at else None,
                    'last_active': u.last_active.isoformat() if u.last_active else None,
                }
                for u in users
            ],
        }
    except Exception as e:
        logger.error(f'Error getting users list: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error getting users list: {str(e)}')


@router.post('/users/{user_id}/update')
async def update_user(
    request: Request,
    user_id: int,
    active: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    user: User = request.state.user

    try:
        target_user = UserOperation.get_user_by_id(db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail='User not found')

        if target_user.id == user.id:
            raise HTTPException(status_code=400, detail='Cannot modify own user status')

        # 準備更新的數據
        update_data = {}

        # 處理 active 參數
        if active is not None:
            if active == 'toggle':
                # 切換當前狀態
                update_data['active'] = not target_user.active
            elif active.lower() == 'true':
                update_data['active'] = True
            elif active.lower() == 'false':
                update_data['active'] = False

        # 處理 role 參數
        if role is not None:
            if role == 'toggle':
                # 切換用戶角色
                update_data['role'] = 'user' if target_user.role == 'admin' else 'admin'
            elif role in ['user', 'admin']:
                update_data['role'] = role

        # 如果有數據需要更新
        if update_data:
            updated_user = UserOperation.update_user(db, user_id, update_data)

            return {
                'status': 'success',
                'message': 'User updated successfully',
                'user': {
                    'id': updated_user.id,
                    'name': updated_user.name,
                    'email': updated_user.email,
                    'active': updated_user.active,
                    'role': updated_user.role,
                },
            }
        else:
            return {'status': 'success', 'message': 'No changes applied'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error updating user: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error updating user: {str(e)}')
