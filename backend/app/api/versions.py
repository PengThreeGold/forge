from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
import os

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.utils.file import format_file_size, ensure_directory_exists, is_safe_filename, sanitize_filename
from app.utils.validation import validate_file_size, validate_version_format
from app.utils.webhook import send_webhook, create_version_publish_webhook_data, create_version_update_webhook_data
from app.crud.webhook_log import crud_webhook_log

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
    如果版本已存在，则添加架构文件到现有版本
    当所有架构文件都上传完成后，设置 is_ready=true
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

    # 验证版本号格式
    if not validate_version_format(version):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本号格式无效，请使用语义版本号格式（如：1.0.0）"
        )

    # 架构映射（用于文件存储和显示）
    arch_mapping = {
        "x86_64": "x86_64",
        "aarch64": "aarch64"
    }
    mapped_architecture = arch_mapping.get(architecture, architecture)

    # 处理 documentation_url，确保是字符串或 None
    doc_url = None
    if documentation_url and documentation_url.strip():
        if documentation_url.startswith(("http://", "https://")):
            doc_url = documentation_url.strip()

    # 验证架构参数
    valid_architectures = ["x86_64", "aarch64"]  # 目前支持的架构
    if architecture not in valid_architectures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的架构类型。支持的架构: {', '.join(valid_architectures)}"
        )

    # 检查版本是否已存在
    existing_version = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version)

    if existing_version:
        # 检查该版本是否已完成（is_ready=true）
        if getattr(existing_version, 'is_ready', False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"版本 {version} 已完成，不允许继续上传文件"
            )

        # 检查该版本是否已存在相同架构的文件
        from app.crud.software_architecture_file import crud_software_architecture_file
        existing_arch_file = crud_software_architecture_file.get_by_version_and_architecture(
            db, version_id=getattr(existing_version, 'id'), architecture=mapped_architecture
        )
        if existing_arch_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"版本 {version} 的 {mapped_architecture} 架构文件已存在"
            )

        # 使用已存在的版本记录，不再创建新版本
        db_version = existing_version
    else:
        # 创建新版本记录
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

    # 验证文件对象
    if not file or not hasattr(file, 'filename') or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件未提供或无效"
        )

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

    # 创建上传目录并保存文件
    try:
        upload_dir = os.path.join(settings.UPLOAD_DIR, space_id, version, mapped_architecture)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, safe_filename)
        file_path = os.path.normpath(file_path)

        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        # 如果文件保存失败，删除已创建的版本记录（如果是新创建的）
        if not existing_version:
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
        architecture=mapped_architecture,
        file_path=file_path,
        file_name=safe_filename,
        file_hash=file_hash
    )

    # 检查是否所有架构都已上传完成
    from app.crud.software_architecture_file import crud_software_architecture_file
    uploaded_architectures = crud_software_architecture_file.get_architectures(db, version_id=getattr(db_version, 'id'))
    required_architectures = ["x86_64", "aarch64"]

    is_ready = all(arch in uploaded_architectures for arch in required_architectures)

    # 如果状态发生变化，更新版本记录
    if is_ready != getattr(db_version, 'is_ready', False):
        db_version = crud.crud_software_version.update(
            db,
            db_obj=db_version,
            obj_in={"is_ready": is_ready}
        )

    # 重新加载版本信息（包含架构文件、总大小、下载次数等）
    db_version = crud.crud_software_version.get_with_download_count(db, version_id=getattr(db_version, 'id'))

    # 确保版本信息完整，添加人类可读的文件大小
    if db_version and hasattr(db_version, 'total_size'):
        db_version.file_size_human = format_file_size(getattr(db_version, 'total_size'))

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
    request: Request,
    version_in: Optional[schemas.SoftwareVersionUpdate] = None,
    architecture: str = Form(None),  # 可选：指定要更新的架构
    file: UploadFile = File(None),   # 可选：新文件
    file_hash: str = Form(None),     # 可选：文件哈希值
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    更新软件版本
    支持更新元数据和替换文件
    如果提供了文件，则会替换指定架构的文件
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

    # 如果没有通过 JSON body 提供 version_in，尝试从 multipart/form-data 的表单中读取元数据
    if version_in is None:
        try:
            form = await request.form()
            form_data = {}
            # 文本字段
            for f in ("version", "release_note", "documentation_url"):
                if f in form and form.get(f) not in (None, ""):
                    form_data[f] = form.get(f)

            # 布尔字段，需要把字符串转换为 bool
            for b in ("is_published", "is_ready"):
                if b in form:
                    val = form.get(b)
                    if isinstance(val, str):
                        if val.lower() in ("true", "1", "yes"):
                            form_data[b] = True
                        elif val.lower() in ("false", "0", "no"):
                            form_data[b] = False
                    else:
                        form_data[b] = bool(val)

            if form_data:
                version_in = schemas.SoftwareVersionUpdate(**form_data)
        except Exception:
            # 无法解析表单或没有表单数据时忽略，继续使用 None
            pass

    # 如果提供了文件，需要验证架构参数
    if file and file.filename:
        if not architecture:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="上传文件时必须指定架构"
            )

        valid_architectures = ["x86_64", "aarch64"]
        if architecture not in valid_architectures:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的架构类型。支持的架构: {', '.join(valid_architectures)}"
            )

    # 检查版本号是否已存在（如果更新了版本号）
    if version_in and version_in.version and version_in.version != getattr(version_obj, 'version'):
        existing_version = crud.crud_software_version.get_by_version(db, space_id=space_id, version=version_in.version)
        if existing_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="版本号已存在"
            )

    # 记录变更（用于Webhook）
    changes = {}

    # 处理文件更新
    if file and file.filename and architecture:
        from app.crud.software_architecture_file import crud_software_architecture_file

        # 验证文件名
        if not is_safe_filename(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件名不安全: {file.filename}"
            )

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

        # 架构映射
        arch_mapping = {"x86_64": "x86_64", "aarch64": "aarch64"}
        mapped_architecture = arch_mapping.get(architecture, architecture)

        # 查找现有的架构文件
        existing_arch_file = crud_software_architecture_file.get_by_version_and_architecture(
            db, version_id=getattr(version_obj, 'id'), architecture=mapped_architecture
        )

        # 删除旧文件（如果存在）
        if existing_arch_file:
            old_file_path = getattr(existing_arch_file, 'file_path')
            normalized_old_path = os.path.normpath(str(old_file_path))
            if os.path.exists(normalized_old_path):
                try:
                    os.remove(normalized_old_path)
                except Exception as e:
                    print(f"警告：删除旧文件失败: {str(e)}")

            # 删除旧的架构文件记录
            crud_software_architecture_file.remove(db, id=getattr(existing_arch_file, 'id'))

        # 创建新的上传目录并保存文件
        try:
            upload_dir = os.path.join(settings.UPLOAD_DIR, space_id, version, mapped_architecture)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, safe_filename)
            file_path = os.path.normpath(file_path)

            with open(file_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件保存失败: {str(e)}"
            )

        # 创建新的架构文件记录
        crud_software_architecture_file.create(
            db=db,
            version_id=getattr(version_obj, 'id'),
            architecture=mapped_architecture,
            file_path=file_path,
            file_name=safe_filename,
            file_hash=file_hash
        )

        changes["file_update"] = {"architecture": mapped_architecture, "file_name": safe_filename}

    # 处理元数据更新
    if version_in:
        if version_in.version and version_in.version != getattr(version_obj, 'version'):
            changes["version"] = {"old": getattr(version_obj, 'version'), "new": version_in.version}
        if version_in.release_note and version_in.release_note != getattr(version_obj, 'release_note'):
            changes["release_note"] = {"old": getattr(version_obj, 'release_note'), "new": version_in.release_note}
        if version_in.documentation_url and version_in.documentation_url != getattr(version_obj, 'documentation_url'):
            changes["documentation_url"] = {"old": getattr(
                version_obj, 'documentation_url'), "new": version_in.documentation_url}
        if version_in.is_published is not None and version_in.is_published != getattr(version_obj, 'is_published'):
            changes["is_published"] = {"old": getattr(version_obj, 'is_published'), "new": version_in.is_published}
        if version_in.is_ready is not None and version_in.is_ready != getattr(version_obj, 'is_ready'):
            changes["is_ready"] = {"old": getattr(version_obj, 'is_ready'), "new": version_in.is_ready}

        # 更新版本记录
        db_version = crud.crud_software_version.update(db, db_obj=version_obj, obj_in=version_in)
    else:
        db_version = version_obj

    # 检查是否所有架构都已上传完成（如果更新了文件）
    if file and architecture:
        from app.crud.software_architecture_file import crud_software_architecture_file
        uploaded_architectures = crud_software_architecture_file.get_architectures(
            db, version_id=getattr(db_version, 'id'))
        required_architectures = ["x86_64", "aarch64"]

        is_ready = all(arch in uploaded_architectures for arch in required_architectures)

        # 如果状态发生变化，更新版本记录
        if is_ready != getattr(db_version, 'is_ready', False):
            db_version = crud.crud_software_version.update(
                db,
                db_obj=db_version,
                obj_in={"is_ready": is_ready}
            )

    # 重新加载版本信息（包含架构文件、总大小、下载次数等）
    db_version = crud.crud_software_version.get_with_download_count(db, version_id=getattr(db_version, 'id'))

    # 添加人类可读的文件大小
    if db_version and hasattr(db_version, 'total_size'):
        db_version.file_size_human = format_file_size(getattr(db_version, 'total_size'))

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

    # 删除文件（现在需要删除整个版本目录，因为按架构组织了）
    import shutil
    version_dir = os.path.join(settings.UPLOAD_DIR, space_id, version)
    normalized_version_dir = os.path.normpath(version_dir)
    if os.path.exists(normalized_version_dir):
        try:
            shutil.rmtree(normalized_version_dir)
        except Exception as e:
            # 如果删除目录失败，记录错误但不阻止删除版本记录
            print(f"警告：删除版本目录失败: {str(e)}")

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
