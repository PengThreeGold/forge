from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import os
import hashlib
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.software_architecture_file import SoftwareArchitectureFile


from typing import Any
from pydantic import BaseModel

from typing import Optional

# 创建一个简单的Pydantic模型用于CRUD
class SoftwareArchitectureFileCreate(BaseModel):
    architecture: str
    file_path: str
    file_name: str
    file_hash: Optional[str] = None

class SoftwareArchitectureFileUpdate(BaseModel):
    pass

class CRUDSoftwareArchitectureFile(CRUDBase[SoftwareArchitectureFile, SoftwareArchitectureFileCreate, SoftwareArchitectureFileUpdate]):
    def __init__(self):
        super().__init__(SoftwareArchitectureFile)
    def get_by_version_id(
        self, db: Session, *, version_id: int
    ) -> List[SoftwareArchitectureFile]:
        """
        根据版本ID获取架构文件列表
        """
        return (
            db.query(self.model)
            .filter(SoftwareArchitectureFile.version_id == version_id)
            .order_by(SoftwareArchitectureFile.architecture)
            .all()
        )
    
    def get_by_version_and_architecture(
        self, db: Session, *, version_id: int, architecture: str
    ) -> Optional[SoftwareArchitectureFile]:
        """
        根据版本ID和架构获取架构文件
        """
        return (
            db.query(self.model)
            .filter(
                SoftwareArchitectureFile.version_id == version_id,
                SoftwareArchitectureFile.architecture == architecture
            )
            .first()
        )
    
    def create(
        self,
        db: Session,
        *,
        version_id: int,
        architecture: str,
        file_path: str,
        file_name: str,
        file_hash: Optional[str] = None
    ) -> SoftwareArchitectureFile:
        """
        创建架构文件
        """
        # 计算文件哈希和大小
        # 确保文件路径使用正确的路径分隔符
        normalized_file_path = os.path.normpath(file_path)
        
        if not file_hash:
            file_hash = self._calculate_file_hash(normalized_file_path)
        file_size = os.path.getsize(normalized_file_path)
        
        # 计算人类可读的文件大小
        from app.utils.file import format_file_size
        file_size_human = format_file_size(file_size)
        
        db_obj = SoftwareArchitectureFile(
            version_id=version_id,
            architecture=architecture,
            file_path=normalized_file_path,
            file_name=file_name,
            file_size=file_size,
            file_hash=file_hash
        )
        
        # 设置人类可读的文件大小（作为属性，不存储在数据库中）
        db_obj.file_size_human = file_size_human
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 重新设置人类可读的文件大小（刷新后可能需要重新设置）
        db_obj.file_size_human = file_size_human
        return db_obj
    
    def increment_download_count(
        self, db: Session, *, architecture_file_id: int
    ) -> SoftwareArchitectureFile:
        """
        增加下载次数
        """
        architecture_file = self.get(db, id=architecture_file_id)
        if architecture_file:
            # 使用SQLAlchemy的更新方式
            db.query(SoftwareArchitectureFile).filter(
                SoftwareArchitectureFile.id == architecture_file_id
            ).update({"download_count": SoftwareArchitectureFile.download_count + 1})
            db.commit()
            db.refresh(architecture_file)
        return architecture_file
    
    def get_total_size(self, db: Session, *, version_id: int) -> int:
        """
        获取版本所有架构文件的总大小
        """
        result = (
            db.query(func.sum(SoftwareArchitectureFile.file_size))
            .filter(SoftwareArchitectureFile.version_id == version_id)
            .scalar()
        )
        return result or 0
    
    def get_total_downloads(self, db: Session, *, version_id: int) -> int:
        """
        获取版本所有架构文件的总下载次数
        """
        result = (
            db.query(func.sum(SoftwareArchitectureFile.download_count))
            .filter(SoftwareArchitectureFile.version_id == version_id)
            .scalar()
        )
        return result or 0
    
    def get_architectures(self, db: Session, *, version_id: int) -> List[str]:
        """
        获取版本支持的架构列表
        """
        result = (
            db.query(SoftwareArchitectureFile.architecture)
            .filter(SoftwareArchitectureFile.version_id == version_id)
            .all()
        )
        return [item[0] for item in result]
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件的MD5哈希值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


# 创建CRUD实例
crud_software_architecture_file = CRUDSoftwareArchitectureFile()