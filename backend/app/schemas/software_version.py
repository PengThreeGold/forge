from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from .software_architecture_file import SoftwareArchitectureFile, PublicSoftwareArchitectureFile


class SoftwareVersionBase(BaseModel):
    version: str = Field(..., min_length=1, max_length=50, description="版本号")
    release_note: Optional[str] = Field(None, description="发布说明")
    documentation_url: Optional[str] = Field(None, description="文档链接")
    is_published: Optional[bool] = Field(False, description="是否已发布")


class SoftwareVersionCreate(SoftwareVersionBase):
    pass


class SoftwareVersionUpdate(BaseModel):
    version: Optional[str] = Field(None, min_length=1, max_length=50, description="版本号")
    release_note: Optional[str] = Field(None, description="发布说明")
    documentation_url: Optional[str] = Field(None, description="文档链接")
    is_published: Optional[bool] = Field(None, description="是否已发布")


class SoftwareVersion(SoftwareVersionBase):
    id: int = Field(..., description="版本ID")
    space_id: str = Field(..., description="软件空间ID")
    architecture_files: List[SoftwareArchitectureFile] = Field([], description="架构文件列表")
    total_size: int = Field(0, description="所有架构文件总大小（字节）")
    total_size_human: Optional[str] = Field(None, description="所有架构文件总大小（人类可读）")
    publish_date: Optional[datetime] = Field(None, description="发布时间")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    total_downloads: int = Field(0, description="所有架构文件总下载次数")

    class Config:
        from_attributes = True


class PublicSoftwareVersion(SoftwareVersionBase):
    id: int = Field(..., description="版本ID")
    version: str = Field(..., description="版本号")
    architecture_files: List[PublicSoftwareArchitectureFile] = Field([], description="架构文件列表")
    total_size_human: Optional[str] = Field(None, description="所有架构文件总大小（人类可读）")
    is_published: bool = Field(..., description="是否已发布")
    publish_date: Optional[datetime] = Field(None, description="发布时间")
    total_downloads: int = Field(0, description="所有架构文件总下载次数")

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    file_path: str = Field(..., description="文件路径")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_hash: str = Field(..., description="文件哈希值")
    file_size_human: str = Field(..., description="人类可读的文件大小")