from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=schemas.ResponseModel[List[dict]])
def read_permissions(
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取系统中所有可用的权限列表
    """
    # 检查权限：只有管理员可以查看权限列表
    if getattr(current_user, 'role') != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 定义权限列表
    permissions = [
        {
            "id": "software:create",
            "name": "创建软件",
            "description": "创建和管理软件空间",
            "category": "软件管理"
        },
        {
            "id": "software:read",
            "name": "查看软件",
            "description": "查看软件空间和版本信息",
            "category": "软件管理"
        },
        {
            "id": "software:update",
            "name": "更新软件",
            "description": "更新软件空间信息",
            "category": "软件管理"
        },
        {
            "id": "software:delete",
            "name": "删除软件",
            "description": "删除软件空间",
            "category": "软件管理"
        },
        {
            "id": "version:create",
            "name": "创建版本",
            "description": "上传和创建软件版本",
            "category": "版本管理"
        },
        {
            "id": "version:read",
            "name": "查看版本",
            "description": "查看软件版本信息",
            "category": "版本管理"
        },
        {
            "id": "version:update",
            "name": "更新版本",
            "description": "更新版本信息",
            "category": "版本管理"
        },
        {
            "id": "version:delete",
            "name": "删除版本",
            "description": "删除软件版本",
            "category": "版本管理"
        },
        {
            "id": "version:publish",
            "name": "发布版本",
            "description": "发布和取消发布版本",
            "category": "版本管理"
        },
        {
            "id": "user:create",
            "name": "创建用户",
            "description": "创建新用户账户",
            "category": "用户管理"
        },
        {
            "id": "user:read",
            "name": "查看用户",
            "description": "查看用户信息",
            "category": "用户管理"
        },
        {
            "id": "user:update",
            "name": "更新用户",
            "description": "更新用户信息",
            "category": "用户管理"
        },
        {
            "id": "user:delete",
            "name": "删除用户",
            "description": "删除用户账户",
            "category": "用户管理"
        },
        {
            "id": "webhook:config",
            "name": "配置Webhook",
            "description": "配置Webhook设置",
            "category": "Webhook管理"
        },
        {
            "id": "webhook:read",
            "name": "查看Webhook日志",
            "description": "查看Webhook调用日志",
            "category": "Webhook管理"
        },
        {
            "id": "stats:read",
            "name": "查看统计",
            "description": "查看系统统计数据",
            "category": "统计分析"
        },
        {
            "id": "stats:space",
            "name": "空间统计",
            "description": "查看软件空间统计",
            "category": "统计分析"
        }
    ]
    
    return schemas.ResponseModel(
        success=True,
        message="获取权限列表成功",
        data=permissions
    )