from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json

from app.core.security import generate_api_key, generate_webhook_secret
from app.crud.base import CRUDBase
from app.models.software_space import SoftwareSpace
from app.schemas.software_space import SoftwareSpaceCreate, SoftwareSpaceUpdate


class CRUDSoftwareSpace(CRUDBase[SoftwareSpace, SoftwareSpaceCreate, SoftwareSpaceUpdate]):
    def get_by_api_key(self, db: Session, *, api_key: str) -> Optional[SoftwareSpace]:
        """
        根据API密钥获取软件空间
        """
        return db.query(SoftwareSpace).filter(SoftwareSpace.api_key == api_key).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[SoftwareSpace]:
        """
        根据名称获取软件空间
        """
        return db.query(SoftwareSpace).filter(SoftwareSpace.name == name).first()

    def create(self, db: Session, *, obj_in: SoftwareSpaceCreate, created_by: int) -> SoftwareSpace:
        """
        创建软件空间
        """
        # 生成唯一的软件空间ID
        space_id = self._generate_unique_space_id(db)
        
        db_obj = SoftwareSpace(
            id=space_id,
            name=obj_in.name,
            description=obj_in.description,
            author=obj_in.author,
            api_key=generate_api_key(),
            webhook_secret=generate_webhook_secret(),
            status=obj_in.status or "active",
            created_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: SoftwareSpace, obj_in: Union[SoftwareSpaceUpdate, Dict[str, Any]]
    ) -> SoftwareSpace:
        """
        更新软件空间
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 处理webhook_events
        if "webhook_events" in update_data and isinstance(update_data["webhook_events"], list):
            update_data["webhook_events"] = json.dumps(update_data["webhook_events"])
        
        # 处理 webhook_url - 直接确保写入的是字符串（无额外校验）
        if "webhook_url" in update_data and update_data["webhook_url"] is not None:
            update_data["webhook_url"] = str(update_data["webhook_url"])
        
        # 如果提供了新的webhook_secret，则重新生成
        if update_data.get("webhook_secret") == "":
            update_data["webhook_secret"] = generate_webhook_secret()
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, created_by: Optional[int] = None
    ) -> List[SoftwareSpace]:
        """
        获取软件空间列表
        """
        query = db.query(self.model)
        if created_by is not None:
            query = query.filter(SoftwareSpace.created_by == created_by)
        return query.offset(skip).limit(limit).all()

    def get_multi_with_stats(
        self, db: Session, *, skip: int = 0, limit: int = 100, created_by: Optional[int] = None
    ) -> List[SoftwareSpace]:
        """
        获取软件空间列表（包含统计信息）
        """
        from app.models.software_version import SoftwareVersion
        from app.models.download_record import DownloadRecord
        
        # 软件版本统计
        version_subquery = db.query(
            SoftwareVersion.space_id,
            func.count(SoftwareVersion.id).label("versions_count")
        ).group_by(SoftwareVersion.space_id).subquery()
        
        # 下载统计
        download_subquery = db.query(
            DownloadRecord.space_id,
            func.count(DownloadRecord.id).label("downloads_count")
        ).group_by(DownloadRecord.space_id).subquery()
        
        query = db.query(
            SoftwareSpace,
            version_subquery.c.versions_count,
            download_subquery.c.downloads_count
        ).outerjoin(
            version_subquery, SoftwareSpace.id == version_subquery.c.space_id
        ).outerjoin(
            download_subquery, SoftwareSpace.id == download_subquery.c.space_id
        )
        
        if created_by is not None:
            query = query.filter(SoftwareSpace.created_by == created_by)
        
        results = query.offset(skip).limit(limit).all()
        
        # 将统计信息添加到软件空间对象
        spaces = []
        for space, versions_count, downloads_count in results:
            space.versions_count = versions_count or 0
            space.downloads_count = downloads_count or 0
            spaces.append(space)
        
        return spaces

    def count(self, db: Session, created_by: Optional[int] = None) -> int:
        """
        获取软件空间总数
        """
        query = db.query(self.model)
        if created_by is not None:
            query = query.filter(SoftwareSpace.created_by == created_by)
        return query.count()

    def get_webhook_events(self, space: SoftwareSpace) -> List[str]:
        """
        获取软件空间的Webhook事件列表
        """
        webhook_events_value = getattr(space, 'webhook_events', None)
        if not webhook_events_value:
            return []
        try:
            return json.loads(webhook_events_value)
        except:
            return []

    def _generate_unique_space_id(self, db: Session) -> str:
        """
        生成唯一的软件空间ID
        """
        from app.core.security import generate_space_id
        
        while True:
            space_id = generate_space_id()
            if not db.query(SoftwareSpace).filter(SoftwareSpace.id == space_id).first():
                return space_id

    def remove(self, db: Session, *, id: str) -> Optional[SoftwareSpace]:
        """
        删除软件空间（支持字符串ID）
        """
        obj = db.query(SoftwareSpace).filter(SoftwareSpace.id == id).first()
        if not obj:
            return None
        
        # 删除数据库记录（级联删除会自动处理所有相关记录）
        db.delete(obj)
        db.commit()
        return obj


# 创建CRUD实例
crud_software_space = CRUDSoftwareSpace(SoftwareSpace)