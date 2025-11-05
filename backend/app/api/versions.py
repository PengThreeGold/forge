from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
import os
import tempfile
import shutil
from datetime import datetime

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.utils.file import format_file_size, calculate_file_hash, ensure_directory_exists, is_safe_filename, sanitize_filename
from app.utils.validation import validate_file_size, validate_version_format
from app.utils.webhook import send_webhook, create_version_publish_webhook_data, create_version_update_webhook_data
from app.crud.webhook_log import crud_webhook_log

router = APIRouter()


@router.get("/{space_id}", response_model=schemas.PaginatedResponse[schemas.SoftwareVersion])
def read_versions(
    space_id: str,
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件版本列表
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    versions = crud.software_version.get_by_space_id(db, space_id=space_id, skip=skip, limit=limit)
    total = crud.software_version.count(db, space_id=space_id)
    
    # 添加下载次数统计
    versions_with_stats = []
    for version in versions:
        version_with_stats = crud.software_version.get_with_download_count(db, version_id=version.id)
        if version_with_stats:
            version_with_stats.file_size_human = format_file_size(version_with_stats.file_size)
        versions_with_stats.append(version_with_stats)
    
    return schemas.PaginatedResponse(
        items=versions_with_stats,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/{space_id}/upload", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
def upload_version(
    space_id: str,
    version: str = Form(...),
    release_note: str = Form(None),
    documentation_url: str = Form(None),
    is_published: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    上传软件版本
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 验证版本号格式
    if not validate_version_format(version):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本号格式无效，请使用语义版本号格式（如：1.0.0）"
        )
    
    # 检查版本是否已存在
    existing_version = crud.software_version.get_by_version(db, space_id=space_id, version=version)
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本已存在"
        )
    
    # 验证文件名
    if not is_safe_filename(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不安全"
        )
    
    # 清理文件名
    safe_filename = sanitize_filename(file.filename)
    
    # 验证文件大小
    file_content = file.file.read()
    file_size = len(file_content)
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大{format_file_size(settings.MAX_FILE_SIZE)}）"
        )
    
    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, space_id, version)
    ensure_directory_exists(upload_dir)
    
    # 保存文件
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 创建版本记录
    version_in = schemas.SoftwareVersionCreate(
        version=version,
        release_note=release_note,
        documentation_url=documentation_url,
        is_published=is_published
    )
    
    db_version = crud.software_version.create(
        db, 
        obj_in=version_in, 
        space_id=space_id,
        file_path=file_path,
        file_name=safe_filename,
        created_by=current_user.id
    )
    
    # 添加人类可读的文件大小
    db_version.file_size_human = format_file_size(db_version.file_size)
    
    # 如果发布了版本，发送Webhook通知
    if is_published and space.webhook_url:
        webhook_events = crud.software_space.get_webhook_events(space)
        if "version_publish" in webhook_events:
            webhook_data = create_version_publish_webhook_data(space_id, version)
            success, response_status, response_body = await send_webhook(
                space.webhook_url,
                "version_publish",
                webhook_data,
                space.webhook_secret
            )
            
            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=space.id,
                event_type="version_publish",
                webhook_url=space.webhook_url,
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )
    
    return schemas.ResponseModel(
        success=True,
        message="版本上传成功",
        data=db_version
    )


@router.put("/{space_id}/{version_id}", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
def update_version(
    space_id: str,
    version_id: int,
    version_in: schemas.SoftwareVersionUpdate,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    更新软件版本
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取版本
    version = crud.software_version.get(db, id=version_id)
    if not version or version.space_id != space_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 检查版本号是否已存在（如果更新了版本号）
    if version_in.version and version_in.version != version.version:
        existing_version = crud.software_version.get_by_version(db, space_id=space_id, version=version_in.version)
        if existing_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="版本号已存在"
            )
    
    # 记录变更（用于Webhook）
    changes = {}
    if version_in.version and version_in.version != version.version:
        changes["version"] = {"old": version.version, "new": version_in.version}
    if version_in.release_note and version_in.release_note != version.release_note:
        changes["release_note"] = {"old": version.release_note, "new": version_in.release_note}
    if version_in.documentation_url and version_in.documentation_url != version.documentation_url:
        changes["documentation_url"] = {"old": version.documentation_url, "new": version_in.documentation_url}
    if version_in.is_published is not None and version_in.is_published != version.is_published:
        changes["is_published"] = {"old": version.is_published, "new": version_in.is_published}
    
    db_version = crud.software_version.update(db, db_obj=version, obj_in=version_in)
    
    # 添加人类可读的文件大小
    db_version.file_size_human = format_file_size(db_version.file_size)
    
    # 发送Webhook通知
    if space.webhook_url and changes:
        webhook_events = crud.software_space.get_webhook_events(space)
        if "version_update" in webhook_events:
            webhook_data = create_version_update_webhook_data(space_id, db_version.version, changes)
            success, response_status, response_body = await send_webhook(
                space.webhook_url,
                "version_update",
                webhook_data,
                space.webhook_secret
            )
            
            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=space.id,
                event_type="version_update",
                webhook_url=space.webhook_url,
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )
    
    return schemas.ResponseModel(
        success=True,
        message="版本更新成功",
        data=db_version
    )


@router.delete("/{space_id}/{version_id}", response_model=schemas.ResponseModel)
def delete_version(
    space_id: str,
    version_id: int,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    删除软件版本
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取版本
    version = crud.software_version.get(db, id=version_id)
    if not version or version.space_id != space_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 删除文件
    if os.path.exists(version.file_path):
        os.remove(version.file_path)
    
    # 删除版本记录
    crud.software_version.remove(db, id=version_id)
    
    return schemas.ResponseModel(
        success=True,
        message="版本删除成功",
        data=None
    )


@router.post("/{space_id}/{version_id}/publish", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
def publish_version(
    space_id: str,
    version_id: int,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    发布软件版本
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取版本
    version = crud.software_version.get(db, id=version_id)
    if not version or version.space_id != space_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 发布版本
    db_version = crud.software_version.publish(db, db_obj=version)
    
    # 发送Webhook通知
    if space.webhook_url:
        webhook_events = crud.software_space.get_webhook_events(space)
        if "version_publish" in webhook_events:
            webhook_data = create_version_publish_webhook_data(space_id, db_version.version)
            success, response_status, response_body = await send_webhook(
                space.webhook_url,
                "version_publish",
                webhook_data,
                space.webhook_secret
            )
            
            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=space.id,
                event_type="version_publish",
                webhook_url=space.webhook_url,
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )
    
    return schemas.ResponseModel(
        success=True,
        message="版本发布成功",
        data=db_version
    )


@router.post("/{space_id}/{version_id}/unpublish", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
def unpublish_version(
    space_id: str,
    version_id: int,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    取消发布软件版本
    """
    # 检查软件空间是否存在和权限
    space = crud.software_space.get(db, id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在"
        )
    
    if current_user.role != "admin" and space.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取版本
    version = crud.software_version.get(db, id=version_id)
    if not version or version.space_id != space_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 取消发布版本
    db_version = crud.software_version.unpublish(db, db_obj=version)
    
    return schemas.ResponseModel(
        success=True,
        message="版本取消发布成功",
        data=db_version
    )