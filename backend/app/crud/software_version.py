from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import os
import hashlib
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.software_version import SoftwareVersion
from app.schemas.software_version import SoftwareVersionCreate, SoftwareVersionUpdate
from app.crud.software_architecture_file import crud_software_architecture_file
from app.utils.file import format_file_size


class CRUDSoftwareVersion(CRUDBase[SoftwareVersion, SoftwareVersionCreate, SoftwareVersionUpdate]):
    def get_by_space_id(
        self, db: Session, *, space_id: str, skip: int = 0, limit: int = 100
    ) -> List[SoftwareVersion]:
        """
        根据软件空间ID获取版本列表
        """
        return (
            db.query(self.model)
            .filter(SoftwareVersion.space_id == space_id)
            .order_by(desc(SoftwareVersion.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_version(self, db: Session, *, space_id: str, version: str) -> Optional[SoftwareVersion]:
        """
        根据软件空间ID和版本号获取版本
        """
        return (
            db.query(self.model)
            .filter(
                SoftwareVersion.space_id == space_id,
                SoftwareVersion.version == version
            )
            .first()
        )

    def get_published_by_space_id(
        self, db: Session, *, space_id: str, skip: int = 0, limit: int = 100
    ) -> List[SoftwareVersion]:
        """
        根据软件空间ID获取已发布的版本列表
        """
        return (
            db.query(self.model)
            .filter(
                SoftwareVersion.space_id == space_id,
                SoftwareVersion.is_published == True
            )
            .order_by(desc(SoftwareVersion.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_published(self, db: Session, *, space_id: str) -> Optional[SoftwareVersion]:
        """
        获取软件空间的最新已发布版本
        """
        return (
            db.query(self.model)
            .filter(
                SoftwareVersion.space_id == space_id,
                SoftwareVersion.is_published == True
            )
            .order_by(desc(SoftwareVersion.publish_date))
            .first()
        )

    def create(
        self,
        db: Session,
        *,
        obj_in: SoftwareVersionCreate,
        space_id: str,
        created_by: int
    ) -> SoftwareVersion:
        """
        创建软件版本
        """
        db_obj = SoftwareVersion(
            space_id=space_id,
            version=obj_in.version,
            release_note=obj_in.release_note,
            documentation_url=obj_in.documentation_url,
            is_published=obj_in.is_published or False,
            publish_date=datetime.utcnow() if obj_in.is_published else None,
            created_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: SoftwareVersion, obj_in: Union[SoftwareVersionUpdate, Dict[str, Any]]
    ) -> SoftwareVersion:
        """
        更新软件版本
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 如果发布状态改变，更新发布时间
        if "is_published" in update_data:
            if update_data["is_published"] and not db_obj.is_published:
                update_data["publish_date"] = datetime.utcnow()
            elif not update_data["is_published"]:
                update_data["publish_date"] = None
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def publish(self, db: Session, *, db_obj: SoftwareVersion) -> SoftwareVersion:
        """
        发布版本
        """
        return self.update(db, db_obj=db_obj, obj_in={"is_published": True})

    def unpublish(self, db: Session, *, db_obj: SoftwareVersion) -> SoftwareVersion:
        """
        取消发布版本
        """
        return self.update(db, db_obj=db_obj, obj_in={"is_published": False})

    def count(self, db: Session, space_id: Optional[str] = None) -> int:
        """
        获取版本总数
        """
        query = db.query(self.model)
        if space_id is not None:
            query = query.filter(SoftwareVersion.space_id == space_id)
        return query.count()

    def get_with_download_count(
        self, db: Session, *, version_id: int
    ) -> Optional[SoftwareVersion]:
        """
        获取版本（包含下载次数和架构文件）
        """
        # 获取版本信息
        version = self.get(db, id=version_id)
        if not version:
            return None
        
        # 获取架构文件
        architecture_files = crud_software_architecture_file.get_by_version_id(db, version_id=version_id)
        
        # 计算总大小和总下载次数
        total_size = sum(af.file_size for af in architecture_files)
        total_downloads = sum(af.download_count for af in architecture_files)
        
        # 添加架构文件信息
        version.architecture_files = architecture_files
        version.total_size = total_size
        version.total_size_human = format_file_size(total_size)
        version.total_downloads = total_downloads
        
        return version

    def delete_version_files(self, db: Session, *, version_id: int) -> bool:
        """
        删除版本关联的所有架构文件
        """
        architecture_files = crud_software_architecture_file.get_by_version_id(db, version_id=version_id)
        success = True
        for af in architecture_files:
            file_path = af.file_path
            if os.path.exists(str(file_path)):
                try:
                    os.remove(str(file_path))
                except Exception:
                    success = False
            db.delete(af)
        
        db.commit()
        return success


# 创建CRUD实例
crud_software_version = CRUDSoftwareVersion(SoftwareVersion)