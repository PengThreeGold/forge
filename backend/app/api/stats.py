from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/system", response_model=schemas.ResponseModel[schemas.SystemStats])
def read_system_stats(
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取系统统计信息（管理员权限）
    """
    if getattr(current_user, 'role') != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取总空间数
    total_spaces = crud.crud_software_space.count(db)
    
    # 获取总版本数
    total_versions = crud.crud_software_version.count(db)
    
    # 获取总下载次数
    total_downloads = crud.crud_download_record.get_total_downloads(db)
    
    # 获取活跃用户数（最近30天有活动的用户）
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(models.User).filter(
        models.User.is_active == True
    ).count()
    
    # 获取最近的空间
    recent_spaces_data = crud.crud_software_space.get_multi_with_stats(
        db, skip=0, limit=5
    )
    recent_spaces = []
    for space in recent_spaces_data:
        recent_spaces.append(schemas.SpaceStats(
            space_id=str(getattr(space, 'id')),
            space_name=str(getattr(space, 'name')),
            total_downloads=getattr(space, 'downloads_count') or 0,
            versions_count=getattr(space, 'versions_count') or 0,
            latest_version=None
        ))
    
    # 获取每日下载统计（最近30天）
    daily_downloads_data = crud.crud_download_record.get_daily_stats(db, days=30)
    daily_downloads = []
    for date, downloads in daily_downloads_data:
        daily_downloads.append({
            "date": date.strftime("%Y-%m-%d"),
            "downloads": downloads
        })
    
    system_stats = schemas.SystemStats(
        total_spaces=total_spaces,
        total_versions=total_versions,
        total_downloads=total_downloads,
        active_users=active_users,
        recent_spaces=recent_spaces,
        daily_downloads=daily_downloads
    )
    
    return schemas.ResponseModel(
        success=True,
        message="获取系统统计信息成功",
        data=system_stats
    )


@router.get("/spaces/{space_id}", response_model=schemas.ResponseModel[schemas.SpaceStats])
def read_space_stats(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间统计信息
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
    
    # 获取统计信息
    total_downloads = crud.crud_download_record.get_total_downloads(db, space_id=space_id)
    versions_count = crud.crud_software_version.count(db, space_id=space_id)
    
    # 获取最新版本
    latest_version_obj = crud.crud_software_version.get_latest_published(db, space_id=space_id)
    latest_version = getattr(latest_version_obj, 'version') if latest_version_obj else None
    
    space_stats = schemas.SpaceStats(
        space_id=str(getattr(space, 'id')),
        space_name=str(getattr(space, 'name')),
        total_downloads=total_downloads,
        versions_count=versions_count,
        latest_version=latest_version
    )
    
    return schemas.ResponseModel(
        success=True,
        message="获取统计信息成功",
        data=space_stats
    )


@router.get("/spaces/{space_id}/downloads/daily", response_model=schemas.ResponseModel[List[schemas.DailyDownloadStats]])
def read_space_daily_downloads(
    space_id: str,
    days: int = Query(30, description="统计天数", le=90),
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间每日下载统计
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
    
    # 获取每日下载统计
    daily_downloads_data = crud.crud_download_record.get_daily_stats(db, space_id=space_id, days=days)
    daily_downloads = []
    for date, downloads in daily_downloads_data:
        daily_downloads.append({
            "date": date.strftime("%Y-%m-%d"),
            "downloads": downloads
        })
    
    return schemas.ResponseModel(
        success=True,
        message="获取每日下载统计成功",
        data=daily_downloads
    )


@router.get("/spaces/{space_id}/downloads/versions", response_model=schemas.ResponseModel[List[schemas.VersionDownloadStats]])
def read_space_version_downloads(
    space_id: str,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取软件空间版本下载统计
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
    
    # 获取版本下载统计
    version_downloads_data = crud.crud_download_record.get_version_stats(db, space_id=space_id)
    version_downloads = []
    for version, downloads in version_downloads_data:
        version_downloads.append({
            "version": version,
            "downloads": downloads
        })
    
    return schemas.ResponseModel(
        success=True,
        message="获取版本下载统计成功",
        data=version_downloads
    )