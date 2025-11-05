from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SpaceStats(BaseModel):
    space_id: str = Field(..., description="软件空间ID")
    space_name: str = Field(..., description="软件空间名称")
    total_downloads: int = Field(..., description="总下载次数")
    versions_count: int = Field(..., description="版本数量")
    latest_version: Optional[str] = Field(None, description="最新版本号")


class DailyDownloadStats(BaseModel):
    date: str = Field(..., description="日期")
    downloads: int = Field(..., description="下载次数")


class VersionDownloadStats(BaseModel):
    version: str = Field(..., description="版本号")
    downloads: int = Field(..., description="下载次数")


class SystemStats(BaseModel):
    total_spaces: int = Field(..., description="总软件空间数")
    total_versions: int = Field(..., description="总版本数")
    total_downloads: int = Field(..., description="总下载次数")
    active_users: int = Field(..., description="活跃用户数")
    recent_spaces: List[SpaceStats] = Field(..., description="最近的软件空间")
    daily_downloads: List[DailyDownloadStats] = Field(..., description="每日下载统计")