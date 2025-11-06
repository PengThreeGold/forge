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
        # 确保传入到 DB 的 documentation_url 是原生字符串或 None，
        # 防止 pydantic 的 HttpUrl 等对象在 SQLite 绑定时报错
        doc_url = None
        if getattr(obj_in, "documentation_url", None) is not None:
            # 使用 str() 可将 HttpUrl 或类似对象转换为字符串
            doc_url = str(obj_in.documentation_url)

        db_obj = SoftwareVersion(
            space_id=space_id,
            version=obj_in.version,
            release_note=obj_in.release_note,
            documentation_url=doc_url,
            is_published=obj_in.is_published or False,
            publish_date=datetime.utcnow() if obj_in.is_published else None,
            created_by=created_by,
            is_ready=False,  # 新创建的版本默认未完成
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # 返回包含统计信息的版本对象
        return self.get_with_download_count(db, version_id=getattr(db_obj, 'id'))

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

        # 如果 documentation_url 在更新数据里，确保它是字符串或 None，避免 pydantic HttpUrl 对象被直接写入 DB
        if "documentation_url" in update_data and update_data["documentation_url"] is not None:
            update_data["documentation_url"] = str(update_data["documentation_url"])

        # 如果发布状态改变，更新发布时间
        if "is_published" in update_data:
            if update_data["is_published"] and not getattr(db_obj, 'is_published'):
                update_data["publish_date"] = datetime.utcnow()
            elif not update_data["is_published"]:
                update_data["publish_date"] = None

        # 如果is_ready状态改变，可以在这里添加相应的逻辑
        if "is_ready" in update_data and update_data["is_ready"] != getattr(db_obj, 'is_ready'):
            # 可以在这里添加版本完成时的额外逻辑
            pass

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

        # 为每个架构文件添加人类可读的文件大小
        for arch_file in architecture_files:
            arch_file.file_size_human = format_file_size(getattr(arch_file, 'file_size'))

        # 计算总大小和总下载次数
        total_size = sum(getattr(af, 'file_size', 0) for af in architecture_files)
        total_downloads = sum(getattr(af, 'download_count', 0) for af in architecture_files)

        # 添加架构文件信息
        version.architecture_files = architecture_files
        version.total_size = total_size
        version.total_size_human = format_file_size(int(total_size))
        version.total_downloads = total_downloads

        return version

    def delete_version_files(self, db: Session, *, version_id: int) -> bool:
        """
        删除版本关联的所有架构文件
        """
        architecture_files = crud_software_architecture_file.get_by_version_id(db, version_id=version_id)
        success = True
        for af in architecture_files:
            file_path = getattr(af, 'file_path')
            normalized_file_path = os.path.normpath(str(file_path))
            if os.path.exists(normalized_file_path):
                try:
                    os.remove(normalized_file_path)
                except Exception:
                    success = False
            db.delete(af)

        db.commit()
        return success


# 创建CRUD实例
crud_software_version = CRUDSoftwareVersion(SoftwareVersion)
