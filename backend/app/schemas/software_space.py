from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class SoftwareSpaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="软件名称")
    description: Optional[str] = Field(None, description="软件描述")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    status: Optional[str] = Field("active", description="软件空间状态")


class SoftwareSpaceCreate(SoftwareSpaceBase):
    pass


class SoftwareSpaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="软件名称")
    description: Optional[str] = Field(None, description="软件描述")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    status: Optional[str] = Field(None, description="软件空间状态")
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook URL")


class SoftwareSpace(SoftwareSpaceBase):
    id: str = Field(..., description="软件空间ID")
    api_key: str = Field(..., description="API密钥")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook密钥")
    webhook_events: Optional[str] = Field(None, description="Webhook事件列表")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    versions_count: Optional[int] = Field(0, description="版本数量")
    downloads_count: Optional[int] = Field(0, description="下载次数")

    class Config:
        from_attributes = True


class PublicSoftwareSpace(BaseModel):
    id: str = Field(..., description="软件空间ID")
    name: str = Field(..., description="软件名称")
    description: Optional[str] = Field(None, description="软件描述")
    author: Optional[str] = Field(None, description="作者")
    created_at: datetime = Field(..., description="创建时间")
    versions_count: Optional[int] = Field(0, description="版本数量")
    latest_version: Optional[str] = Field(None, description="最新版本号")
    total_downloads: Optional[int] = Field(0, description="总下载次数")

    class Config:
        from_attributes = True