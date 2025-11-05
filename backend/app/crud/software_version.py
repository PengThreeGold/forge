from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import os
import hashlib
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.software_version import SoftwareVersion
from app.schemas.software_version import SoftwareVersionCreate, SoftwareVersionUpdate


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
        file_path: str, 
        file_name: str,
        created_by: int
    ) -> SoftwareVersion:
        """
        创建软件版本
        """
        # 计算文件哈希和大小
        file_hash = self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        db_obj = SoftwareVersion(
            space_id=space_id,
            version=obj_in.version,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            file_hash=file_hash,
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
        获取版本（包含下载次数）
        """
        from app.models.download_record import DownloadRecord
        
        download_subquery = db.query(
            DownloadRecord.version_id,
            func.count(DownloadRecord.id).label("download_count")
        ).filter(
            DownloadRecord.version_id == version_id
        ).group_by(DownloadRecord.version_id).subquery()
        
        result = (
            db.query(self.model, download_subquery.c.download_count)
            .outerjoin(download_subquery, SoftwareVersion.id == download_subquery.c.version_id)
            .filter(SoftwareVersion.id == version_id)
            .first()
        )
        
        if not result:
            return None
        
        version, download_count = result
        version.download_count = download_count or 0
        return version

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件的SHA-256哈希值
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


# 创建CRUD实例
crud_software_version = CRUDSoftwareVersion(SoftwareVersion)