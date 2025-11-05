from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import os

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_optional_current_user
from app.utils.webhook import send_webhook, create_download_webhook_data
from app.crud.webhook_log import crud_webhook_log

router = APIRouter()


@router.get("/spaces", response_model=schemas.PaginatedResponse[schemas.PublicSoftwareSpace])
def read_public_spaces(
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="搜索关键词")
) -> Any:
    """
    获取公共软件空间列表
    """
    query = db.query(models.SoftwareSpace).filter(models.SoftwareSpace.status == "active")
    
    if search:
        query = query.filter(
            models.SoftwareSpace.name.contains(search) |
            models.SoftwareSpace.description.contains(search) |
            models.SoftwareSpace.author.contains(search)
        )
    
    total = query.count()
    spaces = query.offset(skip).limit(limit).all()
    
    # 获取统计信息
    public_spaces = []
    for space in spaces:
        # 获取版本数量
        versions_count = db.query(models.SoftwareVersion).filter(
            models.SoftwareVersion.space_id == space.id,
            models.SoftwareVersion.is_published == True
        ).count()
        
        # 获取总下载次数
        total_downloads = crud.crud_download_record.get_total_downloads(db, space_id=getattr(space, 'id'))
        
        # 获取最新版本
        latest_version = crud.crud_software_version.get_latest_published(db, space_id=getattr(space, 'id'))
        
        public_space = schemas.PublicSoftwareSpace(
            id=str(getattr(space, 'id')),
            name=str(getattr(space, 'name')),
            description=str(getattr(space, 'description')) if getattr(space, 'description') else None,
            author=str(getattr(space, 'author')) if getattr(space, 'author') else None,
            created_at=getattr(space, 'created_at'),
            versions_count=versions_count,
            latest_version=getattr(latest_version, 'version') if latest_version else None,
            total_downloads=total_downloads
        )
        public_spaces.append(public_space)
    
    return schemas.PaginatedResponse(
        items=public_spaces,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/spaces/{space_id}", response_model=schemas.ResponseModel[schemas.PublicSoftwareSpace])
def read_public_space(
    space_id: str,
    db: Session = Depends(get_current_db)
) -> Any:
    """
    获取公共软件空间详情
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space or getattr(space, 'status') != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在或未激活"
        )
    
    # 获取版本数量
    versions_count = db.query(models.SoftwareVersion).filter(
        models.SoftwareVersion.space_id == space.id,
        models.SoftwareVersion.is_published == True
    ).count()
    
    # 获取总下载次数
    total_downloads = crud.crud_download_record.get_total_downloads(db, space_id=getattr(space, 'id'))
    
    # 获取最新版本
    latest_version = crud.crud_software_version.get_latest_published(db, space_id=getattr(space, 'id'))
    
    public_space = schemas.PublicSoftwareSpace(
        id=str(getattr(space, 'id')),
        name=str(getattr(space, 'name')),
        description=str(getattr(space, 'description')) if getattr(space, 'description') else None,
        author=str(getattr(space, 'author')) if getattr(space, 'author') else None,
        created_at=getattr(space, 'created_at'),
        versions_count=versions_count,
        latest_version=getattr(latest_version, 'version') if latest_version else None,
        total_downloads=total_downloads
    )
    
    return schemas.ResponseModel(
        success=True,
        message="获取软件空间详情成功",
        data=public_space
    )


@router.get("/spaces/{space_id}/versions", response_model=schemas.PaginatedResponse[schemas.PublicSoftwareVersion])
def read_public_versions(
    space_id: str,
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    获取软件空间的已发布版本列表
    """
    space = crud.crud_software_space.get(db, id=space_id)
    if not space or getattr(space, 'status') != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在或未激活"
        )
    
    versions = crud.crud_software_version.get_published_by_space_id(
        db, space_id=space_id, skip=skip, limit=limit
    )
    total = db.query(models.SoftwareVersion).filter(
        models.SoftwareVersion.space_id == space_id,
        models.SoftwareVersion.is_published == True
    ).count()
    
    # 转换为公共版本格式
    public_versions = []
    for version in versions:
        version_with_stats = crud.crud_software_version.get_with_download_count(db, version_id=getattr(version, 'id'))
        if version_with_stats:
            from app.utils.file import format_file_size
            version_with_stats.file_size_human = format_file_size(version_with_stats.file_size)
        
        public_version = schemas.PublicSoftwareVersion(
            id=getattr(version, 'id'),
            version=getattr(version, 'version'),
            file_size_human=getattr(version_with_stats, 'file_size_human') if version_with_stats else format_file_size(getattr(version, 'file_size')),
            release_note=getattr(version, 'release_note'),
            documentation_url=getattr(version, 'documentation_url'),
            publish_date=getattr(version, 'publish_date'),
            download_count=getattr(version_with_stats, 'download_count') if version_with_stats else 0
        )
        public_versions.append(public_version)
    
    return schemas.PaginatedResponse(
        items=public_versions,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/download/{space_id}/{version_id}")
async def download_version(
    space_id: str,
    version_id: int,
    api_key: Optional[str] = Query(None, description="API密钥"),
    request: Request,
    db: Session = Depends(get_current_db)
) -> Any:
    """
    下载软件版本
    """
    # 验证API密钥
    space = None
    if api_key:
        space = crud.crud_software_space.get_by_api_key(db, api_key=api_key)
    
    if not space or getattr(space, 'id') != space_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    
    if getattr(space, 'status') != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在或未激活"
        )
    
    # 获取版本信息
    version = crud.crud_software_version.get(db, id=version_id)
    if not version or getattr(version, 'space_id') != space_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    if not getattr(version, 'is_published'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本未发布"
        )
    
    # 检查文件是否存在
    if not os.path.exists(getattr(version, 'file_path')):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 获取客户端IP
    client_ip = request.client.host if request.client else "127.0.0.1"
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # 获取用户代理
    user_agent = request.headers.get("user-agent", "")
    
    # 获取来源页面
    referer = request.headers.get("referer", "")
    
    # 记录下载
    download_record = crud.crud_download_record.create(
        db=db,
        space_id=space_id,
        version_id=version_id,
        ip_address=client_ip,
        user_agent=user_agent,
        referer=referer
    )
    
    # 发送Webhook通知
    if getattr(space, 'webhook_url'):
        webhook_events = crud.crud_software_space.get_webhook_events(space)
        if "download" in webhook_events:
            webhook_data = create_download_webhook_data(space_id, getattr(version, 'version'), client_ip)
            success, response_status, response_body = await send_webhook(
                getattr(space, 'webhook_url'),
                "download",
                webhook_data,
                getattr(space, 'webhook_secret')
            )
            
            # 记录Webhook日志
            crud_webhook_log.create(
                db=db,
                space_id=getattr(space, 'id'),
                event_type="download",
                webhook_url=getattr(space, 'webhook_url'),
                payload=str(webhook_data),
                response_status=response_status,
                response_body=response_body
            )
    
    # 返回文件
    return FileResponse(
        path=version.file_path,
        filename=version.file_name,
        media_type='application/octet-stream'
    )


@router.get("/spaces/{space_id}/latest")
def download_latest_version(
    space_id: str,
    request: Request,
    api_key: Optional[str] = Query(None, description="API密钥"),
    db: Session = Depends(get_current_db)
) -> Any:
    """
    下载最新版本
    """
    # 验证API密钥
    space = None
    if api_key:
        space = crud.crud_software_space.get_by_api_key(db, api_key=api_key)
    
    if not space or getattr(space, 'id') != space_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    
    if getattr(space, 'status') != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="软件空间不存在或未激活"
        )
    
    # 获取最新版本
    latest_version = crud.crud_software_version.get_latest_published(db, space_id=space_id)
    if not latest_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有已发布的版本"
        )
    
    # 重定向到下载链接
    return {
        "redirect": f"/api/public/download/{space_id}/{latest_version.id}"
    }