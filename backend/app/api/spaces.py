from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user, get_current_admin_user
from app.utils.webhook import send_webhook, create_space_update_webhook_data
from app.crud.webhook_log import crud_webhook_log

router = APIRouter()


@router.get("/", response_model=schemas.PaginatedResponse[schemas.SoftwareSpace])
def read_spaces(
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间列表
    """
    # 管理员可以查看所有空间，普通用户只能查看自己创建的空间
    if getattr(current_user, 'role') == "admin":
        spaces = crud.crud_software_space.get_multi_with_stats(db, skip=skip, limit=limit)
        total = crud.crud_software_space.count(db)
    else:
        spaces = crud.crud_software_space.get_multi_with_stats(db, skip=skip, limit=limit, created_by=getattr(current_user, 'id'))
        total = crud.crud_software_space.count(db, created_by=getattr(current_user, 'id'))
    
    # 使用 Pydantic schema 序列化空间数据列表
    space_data_list = [schemas.SoftwareSpace.from_orm(space) for space in spaces]
    
    return schemas.PaginatedResponse(
        items=space_data_list,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=schemas.ResponseModel[schemas.SoftwareSpace])
def create_space(
    *,
    db: Session = Depends(get_current_db),
    space_in: schemas.SoftwareSpaceCreate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    创建软件空间
    """
    # 检查名称是否已存在
    existing_space = crud.crud_software_space.get_by_name(db, name=space_in.name)
    if existing_space:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="软件名称已存在"
        )
    
    space = crud.crud_software_space.create(db, obj_in=space_in, created_by=getattr(current_user, 'id'))
    
    # 使用 Pydantic schema 序列化空间数据
    space_data = schemas.SoftwareSpace.from_orm(space)
    
    return schemas.ResponseModel(
        success=True,
        message="软件空间创建成功",
        data=space_data
    )


@router.get("/{space_id}", response_model=schemas.ResponseModel[schemas.SoftwareSpace])
def read_space(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间详情
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    # 检查权限：管理员可以查看所有空间，普通用户只能查看自己创建的空间
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取统计信息
    space_with_stats = crud.crud_software_space.get_multi_with_stats(
        db, skip=0, limit=1, created_by=getattr(current_user, 'id') if getattr(current_user, 'role') != "admin" else None
    )
    for s in space_with_stats:
        if getattr(s, 'id') == space_id:
            space = s
            break
    
    # 使用 Pydantic schema 序列化空间数据
    space_data = schemas.SoftwareSpace.from_orm(space)
    
    return schemas.ResponseModel(
        success=True,
        message="获取软件空间详情成功",
        data=space_data
    )


@router.put("/{space_id}", response_model=schemas.ResponseModel[schemas.SoftwareSpace])
async def update_space(
    space_id: str,
    space_in: schemas.SoftwareSpaceUpdate,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    更新软件空间
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    # 检查权限：管理员可以更新所有空间，普通用户只能更新自己创建的空间
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 检查名称是否已存在（如果更新了名称）
    if space_in.name and space_in.name != space.name:
        existing_space = crud.crud_software_space.get_by_name(db, name=space_in.name)
        if existing_space:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="软件名称已存在"
            )
    
    # 记录变更（用于Webhook）
    changes = {}
    if space_in.name and space_in.name != space.name:
        changes["name"] = {"old": space.name, "new": space_in.name}
    if space_in.description and space_in.description != space.description:
        changes["description"] = {"old": space.description, "new": space_in.description}
    if space_in.author and space_in.author != space.author:
        changes["author"] = {"old": space.author, "new": space_in.author}
    if space_in.status and space_in.status != space.status:
        changes["status"] = {"old": space.status, "new": space_in.status}
    
    space = crud.crud_software_space.update(db, db_obj=space, obj_in=space_in)
    
    # 发送Webhook通知
    if getattr(space, 'webhook_url') and changes:
        webhook_events = crud.crud_software_space.get_webhook_events(space)
        if "space_update" in webhook_events:
            webhook_data = create_space_update_webhook_data(getattr(space, 'id'), changes)
            success, response_status, response_body = await send_webhook(
                getattr(space, 'webhook_url'),
                "space_update",
                webhook_data,
                getattr(space, 'webhook_secret')
            )
            
            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=getattr(space, 'id'),
                event_type="space_update",
                webhook_url=getattr(space, 'webhook_url'),
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )
    
    # 使用 Pydantic schema 序列化空间数据
    space_data = schemas.SoftwareSpace.from_orm(space)
    
    return schemas.ResponseModel(
        success=True,
        message="软件空间更新成功",
        data=space_data
    )


@router.delete("/{space_id}", response_model=schemas.ResponseModel)
def delete_space(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    删除软件空间
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    # 检查权限：管理员可以删除所有空间，普通用户只能删除自己创建的空间
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    crud.crud_software_space.remove(db, id=space_id)
    
    return schemas.ResponseModel(
        success=True,
        message="软件空间删除成功",
        data=None
    )


@router.get("/{space_id}/stats", response_model=schemas.ResponseModel[schemas.SpaceStats])
def get_space_stats(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间统计信息
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    # 检查权限
    if getattr(current_user, 'role') != "admin" and getattr(space, 'created_by') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取统计信息
    total_downloads = crud.crud_download_record.get_total_downloads(db, space_id=space_id)
    versions_count = crud.crud_software_version.count(db, space_id=space_id)
    
    # 获取最新版本
    latest_version_obj = crud.crud_software_version.get_latest_published(db, space_id=space_id)
    latest_version = getattr(latest_version_obj, 'version') if latest_version_obj else None
    
    stats = schemas.SpaceStats(
        space_id=getattr(space, 'id'),
        space_name=getattr(space, 'name'),
        total_downloads=total_downloads,
        versions_count=versions_count,
        latest_version=latest_version
    )
    
    return schemas.ResponseModel(
        success=True,
        message="获取统计信息成功",
        data=stats
    )