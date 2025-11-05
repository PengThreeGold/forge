from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user
from app.core.security import generate_webhook_secret

router = APIRouter()


@router.get("/{space_id}/config", response_model=schemas.ResponseModel[schemas.WebhookConfig])
def read_webhook_config(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取Webhook配置
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取Webhook事件列表
    webhook_events = crud.crud_software_space.get_webhook_events(space)
    
    # 隐藏部分Webhook密钥
    webhook_secret = None
    if getattr(space, 'webhook_secret'):
        webhook_secret = getattr(space, 'webhook_secret')[:4] + "****" + getattr(space, 'webhook_secret')[-4:]
    
    webhook_config = schemas.WebhookConfig(
        webhook_url=getattr(space, 'webhook_url'),
        webhook_secret=webhook_secret,
        webhook_events=webhook_events
    )
    
    return schemas.ResponseModel(
        success=True,
        message="获取Webhook配置成功",
        data=webhook_config
    )


@router.put("/{space_id}/config", response_model=schemas.ResponseModel)
def update_webhook_config(
    space_id: str,
    webhook_config: schemas.WebhookConfigUpdate,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    更新Webhook配置
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 准备更新数据
    update_data = {}
    
    if webhook_config.webhook_url is not None:
        update_data["webhook_url"] = webhook_config.webhook_url
    
    if webhook_config.webhook_secret is not None:
        # 如果提供了空的密钥，则重新生成
        if webhook_config.webhook_secret == "":
            update_data["webhook_secret"] = generate_webhook_secret()
        else:
            update_data["webhook_secret"] = webhook_config.webhook_secret
    
    if webhook_config.webhook_events is not None:
        update_data["webhook_events"] = webhook_config.webhook_events
    
    # 更新软件空间
    space = crud.crud_software_space.update(db, db_obj=space, obj_in=update_data)
    
    return schemas.ResponseModel(
        success=True,
        message="Webhook配置更新成功",
        data=None
    )


@router.post("/{space_id}/regenerate-secret", response_model=schemas.ResponseModel[dict])
def regenerate_webhook_secret(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    重新生成Webhook密钥
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 生成新的Webhook密钥
    new_secret = generate_webhook_secret()
    
    # 更新软件空间
    space = crud.crud_software_space.update(
        db,
        db_obj=space,
        obj_in={"webhook_secret": new_secret}
    )
    
    return schemas.ResponseModel(
        success=True,
        message="Webhook密钥重新生成成功",
        data={"webhook_secret": new_secret}
    )


@router.get("/{space_id}/logs", response_model=schemas.PaginatedResponse[schemas.WebhookLog])
def read_webhook_logs(
    space_id: str,
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取Webhook日志
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取Webhook日志
    logs = crud.crud_webhook_log.get_by_space_id(
        db, space_id=space_id, skip=skip, limit=limit
    )
    total = crud.crud_webhook_log.count(db, space_id=space_id)
    
    # 添加软件空间名称
    logs_with_space_name = []
    for log in logs:
        # 使用 Pydantic schema 序列化日志数据，手动创建对象
        log_with_space_name = schemas.WebhookLog(
            id=getattr(log, 'id'),
            space_name=getattr(space, 'name'),
            event_type=getattr(log, 'event_type'),
            payload=getattr(log, 'payload'),
            response_status=getattr(log, 'response_status'),
            response_body=getattr(log, 'response_body'),
            attempt_time=getattr(log, 'attempt_time')
        )
        logs_with_space_name.append(log_with_space_name)
    
    return schemas.PaginatedResponse(
        items=logs_with_space_name,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{space_id}/logs/failed", response_model=schemas.PaginatedResponse[schemas.WebhookLog])
def read_failed_webhook_logs(
    space_id: str,
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取失败的Webhook日志
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取失败的Webhook日志
    logs = crud.crud_webhook_log.get_failed_logs(
        db, space_id=space_id, skip=skip, limit=limit
    )
    
    # 获取失败日志总数
    from sqlalchemy import func
    total = db.query(models.WebhookLog).filter(
        models.WebhookLog.space_id == space_id,
        models.WebhookLog.response_status >= 400
    ).count()
    
    # 添加软件空间名称
    logs_with_space_name = []
    for log in logs:
        # 使用 Pydantic schema 序列化日志数据，手动创建对象
        log_with_space_name = schemas.WebhookLog(
            id=getattr(log, 'id'),
            space_name=getattr(space, 'name'),
            event_type=getattr(log, 'event_type'),
            payload=getattr(log, 'payload'),
            response_status=getattr(log, 'response_status'),
            response_body=getattr(log, 'response_body'),
            attempt_time=getattr(log, 'attempt_time')
        )
        logs_with_space_name.append(log_with_space_name)
    
    return schemas.PaginatedResponse(
        items=logs_with_space_name,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{space_id}/logs/events/{event_type}", response_model=schemas.PaginatedResponse[schemas.WebhookLog])
def read_webhook_logs_by_event_type(
    space_id: str,
    event_type: str,
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    根据事件类型获取Webhook日志
    """
    # 检查软件空间是否存在和权限
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取指定事件类型的Webhook日志
    logs = crud.crud_webhook_log.get_by_event_type(
        db, event_type=event_type, skip=skip, limit=limit
    )
    
    # 过滤出属于当前空间的日志
    filtered_logs = []
    for log in logs:
        if str(getattr(log, 'space_id')) == space_id:
            filtered_logs.append(log)
    
    # 限制数量
    logs = filtered_logs[skip:skip+limit]
    total = len(filtered_logs)
    
    # 添加软件空间名称
    logs_with_space_name = []
    for log in logs:
        # 使用 Pydantic schema 序列化日志数据，手动创建对象
        log_with_space_name = schemas.WebhookLog(
            id=getattr(log, 'id'),
            space_name=getattr(space, 'name'),
            event_type=getattr(log, 'event_type'),
            payload=getattr(log, 'payload'),
            response_status=getattr(log, 'response_status'),
            response_body=getattr(log, 'response_body'),
            attempt_time=getattr(log, 'attempt_time')
        )
        logs_with_space_name.append(log_with_space_name)
    
    return schemas.PaginatedResponse(
        items=logs_with_space_name,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )