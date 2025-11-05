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
import json

router = APIRouter()


@router.get("/{space_id}/versions", response_model=schemas.PaginatedResponse[schemas.SoftwareVersion])
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

    versions = crud.crud_software_version.get_by_space_id(db, space_id=space_id, skip=skip, limit=limit)
    total = crud.crud_software_version.count(db, space_id=space_id)

    # 添加下载次数统计
    versions_with_stats = []
    for version in versions:
        version_with_stats = crud.crud_software_version.get_with_download_count(db, version_id=getattr(version, 'id'))
        versions_with_stats.append(version_with_stats)

    # 使用 Pydantic schema 序列化版本数据列表
    version_data_list = [schemas.SoftwareVersion.from_orm(version) for version in versions_with_stats]
    
    return schemas.PaginatedResponse(
        items=version_data_list,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/{space_id}/versions", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
async def create_version(
    space_id: str,
    version: str = Form(...),
    architecture: str = Form(...),  # 指定架构：x86_64 或 aarch64
    release_note: str = Form(None),
    documentation_url: str = Form(None),
    is_published: bool = Form(False),
    file: UploadFile = File(...),  # 单文件上传，必填
    file_hash: str = Form(None),   # 文件哈希值
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    创建软件版本（支持多架构）
    """
    import json

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

    # 验证版本号格式
    if not validate_version_format(version):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本号格式无效，请使用语义版本号格式（如：1.0.0）"
        )

    # 检查版本是否已存在
    existing_version = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本已存在"
        )

    # 验证架构参数
    valid_architectures = ["x86_64", "aarch64"]  # 目前支持的架构
    if architecture not in valid_architectures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的架构类型。支持的架构: {', '.join(valid_architectures)}"
        )
    
    # 架构映射（用于文件存储和显示）
    arch_mapping = {
        "x86_64": "x86_64",
        "aarch64": "aarch64"
    }
    mapped_architecture = arch_mapping.get(architecture, architecture)

    # 验证文件对象
    if not file or not hasattr(file, 'filename') or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件未提供或无效"
        )

    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, space_id, version)
    ensure_directory_exists(upload_dir)

    # 验证文件名
    if not is_safe_filename(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件名不安全: {file.filename}"
        )

    # 清理文件名
    safe_filename = sanitize_filename(file.filename)

    # 读取文件内容
    try:
        file_content = file.file.read()
        file_size = len(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件读取失败: {str(e)}"
        )

    # 验证文件大小
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大{format_file_size(settings.MAX_FILE_SIZE)}）"
        )

    # 处理 documentation_url，确保是有效的 URL 或 None
    doc_url = None
    if documentation_url and documentation_url.strip():
        try:
            from pydantic import HttpUrl
            # 验证URL格式
            if documentation_url.startswith(('http://', 'https://')):
                doc_url = HttpUrl(documentation_url)
            else:
                # 如果不是有效的URL格式，设置为None
                doc_url = None
        except:
            # 如果 URL 无效，设置为 None
            doc_url = None
    
    # 创建版本记录
    version_in = schemas.SoftwareVersionCreate(
        version=version,
        release_note=release_note,
        documentation_url=doc_url,
        is_published=is_published
    )

    db_version = crud.crud_software_version.create(
        db,
        obj_in=version_in,
        space_id=space_id,
        created_by=getattr(current_user, 'id')
    )

    # 创建上传目录（在版本记录创建后）
    try:
        upload_dir = os.path.join(settings.UPLOAD_DIR, space_id, version)
        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, safe_filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        # 如果文件保存失败，删除已创建的版本记录
        crud.crud_software_version.remove(db, id=getattr(db_version, 'id'))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )

    # 创建架构文件记录
    from app.crud.software_architecture_file import crud_software_architecture_file
    crud_software_architecture_file.create(
        db=db,
        version_id=getattr(db_version, 'id'),
        architecture=mapped_architecture,  # 使用映射后的架构名称
        file_path=file_path,
        file_name=safe_filename,
        file_hash=file_hash
    )

    # 重新加载版本信息（包含架构文件）
    db_version = crud.crud_software_version.get_with_download_count(db, version_id=getattr(db_version, 'id'))

    # 如果发布了版本，发送Webhook通知
    if is_published and getattr(space, 'webhook_url'):
        webhook_events = crud.crud_software_space.get_webhook_events(space)
        if "version_publish" in webhook_events:
            webhook_data = create_version_publish_webhook_data(space_id, version)
            success, response_status, response_body = await send_webhook(
                getattr(space, 'webhook_url'),
                "version_publish",
                webhook_data,
                getattr(space, 'webhook_secret') if getattr(space, 'webhook_secret') else None
            )

            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=getattr(space, 'id'),
                event_type="version_publish",
                webhook_url=getattr(space, 'webhook_url'),
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )

    # 使用 Pydantic schema 序列化版本数据
    version_data = schemas.SoftwareVersion.from_orm(db_version)
    
    return schemas.ResponseModel(
        success=True,
        message="版本上传成功",
        data=version_data
    )


@router.put("/{space_id}/versions/{version}", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
async def update_version(
    space_id: str,
    version: str,
    version_in: schemas.SoftwareVersionUpdate,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    更新软件版本
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

    # 获取版本
    version_obj = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)
    if not version_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )

    # 检查版本号是否已存在（如果更新了版本号）
    if version_in.version and version_in.version != getattr(version_obj, 'version'):
        existing_version = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version_in.version)
        if existing_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="版本号已存在"
            )

    # 记录变更（用于Webhook）
    changes = {}
    if version_in.version and version_in.version != getattr(version_obj, 'version'):
        changes["version"] = {"old": getattr(version_obj, 'version'), "new": version_in.version}
    if version_in.release_note and version_in.release_note != getattr(version_obj, 'release_note'):
        changes["release_note"] = {"old": getattr(version_obj, 'release_note'), "new": version_in.release_note}
    if version_in.documentation_url and version_in.documentation_url != getattr(version_obj, 'documentation_url'):
        changes["documentation_url"] = {"old": getattr(
            version_obj, 'documentation_url'), "new": version_in.documentation_url}
    if version_in.is_published is not None and version_in.is_published != getattr(version_obj, 'is_published'):
        changes["is_published"] = {"old": getattr(version_obj, 'is_published'), "new": version_in.is_published}

    db_version = crud.crud_software_version.update(db, db_obj=version_obj, obj_in=version_in)

    # 添加人类可读的文件大小
    db_version.file_size_human = format_file_size(getattr(db_version, 'file_size'))

    # 发送Webhook通知
    if getattr(space, 'webhook_url') and changes:
        webhook_events = crud.crud_software_space.get_webhook_events(space)
        if "version_update" in webhook_events:
            webhook_data = create_version_update_webhook_data(space_id, getattr(db_version, 'version'), changes)
            success, response_status, response_body = await send_webhook(
                getattr(space, 'webhook_url'),
                "version_update",
                webhook_data,
                getattr(space, 'webhook_secret')
            )

            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=getattr(space, 'id'),
                event_type="version_update",
                webhook_url=getattr(space, 'webhook_url'),
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )

    # 使用 Pydantic schema 序列化版本数据
    version_data = schemas.SoftwareVersion.from_orm(db_version)
    
    return schemas.ResponseModel(
        success=True,
        message="版本更新成功",
        data=version_data
    )


@router.delete("/{space_id}/versions/{version}", response_model=schemas.ResponseModel)
def delete_version(
    space_id: str,
    version: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    删除软件版本
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

    # 获取版本
    version_obj = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)
    if not version_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )

    # 删除文件
    if os.path.exists(getattr(version_obj, 'file_path')):
        os.remove(getattr(version_obj, 'file_path'))

    # 删除版本记录
    crud.crud_software_version.remove(db, id=getattr(version_obj, 'id'))

    return schemas.ResponseModel(
        success=True,
        message="版本删除成功",
        data=None
    )


@router.post("/{space_id}/versions/{version}/publish", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
async def publish_version(
    space_id: str,
    version: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    发布软件版本
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

    # 获取版本
    version_obj = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)
    if not version_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )

    # 发布版本
    db_version = crud.crud_software_version.publish(db, db_obj=version_obj)

    # 发送Webhook通知
    if getattr(space, 'webhook_url'):
        webhook_events = crud.crud_software_space.get_webhook_events(space)
        if "version_publish" in webhook_events:
            webhook_data = create_version_publish_webhook_data(space_id, version)
            success, response_status, response_body = await send_webhook(
                getattr(space, 'webhook_url'),
                "version_publish",
                webhook_data,
                getattr(space, 'webhook_secret')
            )

            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=getattr(space, 'id'),
                event_type="version_publish",
                webhook_url=getattr(space, 'webhook_url'),
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )

    # 使用 Pydantic schema 序列化版本数据
    version_data = schemas.SoftwareVersion.from_orm(db_version)
    
    return schemas.ResponseModel(
        success=True,
        message="版本发布成功",
        data=version_data
    )


@router.post("/{space_id}/versions/{version}/unpublish", response_model=schemas.ResponseModel[schemas.SoftwareVersion])
def unpublish_version(
    space_id: str,
    version: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    取消发布软件版本
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

    # 获取版本
    version_obj = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)
    if not version_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )

    # 取消发布版本
    db_version = crud.crud_software_version.unpublish(db, db_obj=version_obj)

    # 使用 Pydantic schema 序列化版本数据
    version_data = schemas.SoftwareVersion.from_orm(db_version)
    
    return schemas.ResponseModel(
        success=True,
        message="版本取消发布成功",
        data=version_data
    )
