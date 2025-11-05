from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DownloadRecord(BaseModel):
    id: int = Field(..., description="下载记录ID")
    space_name: str = Field(..., description="软件空间名称")
    version: str = Field(..., description="版本号")
    ip_address: str = Field(..., description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    download_time: datetime = Field(..., description="下载时间")

    class Config:
        from_attributes = True