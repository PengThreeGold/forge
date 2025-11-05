from typing import Optional
from pydantic import BaseModel, Field


class SoftwareArchitectureFileBase(BaseModel):
    architecture: str = Field(..., description="系统架构")
    file_name: str = Field(..., description="文件名")


class SoftwareArchitectureFileCreate(SoftwareArchitectureFileBase):
    file_hash: Optional[str] = Field(None, description="文件MD5哈希值")


class SoftwareArchitectureFile(SoftwareArchitectureFileBase):
    id: int = Field(..., description="架构文件ID")
    file_path: str = Field(..., description="文件路径（仅管理员接口返回）")
    file_size: int = Field(..., description="文件大小（字节）")
    file_size_human: Optional[str] = Field(None, description="人类可读的文件大小")
    file_hash: str = Field(..., description="文件MD5哈希值，用于完整性校验")
    download_count: int = Field(0, description="下载次数")

    class Config:
        from_attributes = True


class PublicSoftwareArchitectureFile(SoftwareArchitectureFileBase):
    id: int = Field(..., description="架构文件ID")
    file_size_human: Optional[str] = Field(None, description="人类可读的文件大小")
    file_hash: str = Field(..., description="文件MD5哈希值，用于完整性校验")
    download_count: int = Field(0, description="下载次数")

    class Config:
        from_attributes = True