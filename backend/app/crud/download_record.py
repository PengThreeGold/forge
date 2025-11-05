from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.crud.base import CRUDBase
from app.models.download_record import DownloadRecord


class CRUDDownloadRecord(CRUDBase[DownloadRecord, dict, dict]):
    def create(
        self,
        db: Session,
        *,
        space_id: str,
        version_id: int,
        ip_address: str,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None
    ) -> DownloadRecord:
        """
        创建下载记录
        """
        db_obj = DownloadRecord(
            space_id=space_id,
            version_id=version_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_space_id(
        self,
        db: Session,
        *,
        space_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DownloadRecord]:
        """
        根据软件空间ID获取下载记录
        """
        return (
            db.query(self.model)
            .filter(DownloadRecord.space_id == space_id)
            .order_by(desc(DownloadRecord.download_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_version_id(
        self,
        db: Session,
        *,
        version_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[DownloadRecord]:
        """
        根据版本ID获取下载记录
        """
        return (
            db.query(self.model)
            .filter(DownloadRecord.version_id == version_id)
            .order_by(desc(DownloadRecord.download_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_daily_stats(
        self,
        db: Session,
        *,
        space_id: Optional[str] = None,
        days: int = 30
    ) -> List[dict]:
        """
        获取每日下载统计
        """
        from sqlalchemy import extract, date
        
        query = db.query(
            func.date(DownloadRecord.download_time).label('date'),
            func.count(DownloadRecord.id).label('downloads')
        )
        
        if space_id is not None:
            query = query.filter(DownloadRecord.space_id == space_id)
        
        return (
            query.group_by(func.date(DownloadRecord.download_time))
            .order_by(desc(func.date(DownloadRecord.download_time)))
            .limit(days)
            .all()
        )

    def get_version_stats(
        self,
        db: Session,
        *,
        space_id: Optional[str] = None
    ) -> List[dict]:
        """
        获取版本下载统计
        """
        from app.models.software_version import SoftwareVersion
        
        query = db.query(
            SoftwareVersion.version,
            func.count(DownloadRecord.id).label('downloads')
        ).join(
            DownloadRecord, SoftwareVersion.id == DownloadRecord.version_id
        )
        
        if space_id is not None:
            query = query.filter(SoftwareVersion.space_id == space_id)
        
        return (
            query.group_by(SoftwareVersion.id, SoftwareVersion.version)
            .order_by(desc(func.count(DownloadRecord.id)))
            .all()
        )

    def get_total_downloads(
        self,
        db: Session,
        *,
        space_id: Optional[str] = None,
        version_id: Optional[int] = None
    ) -> int:
        """
        获取总下载次数
        """
        query = db.query(func.count(DownloadRecord.id))
        
        if space_id is not None:
            query = query.filter(DownloadRecord.space_id == space_id)
        
        if version_id is not None:
            query = query.filter(DownloadRecord.version_id == version_id)
        
        return query.scalar() or 0

    def count(self, db: Session, space_id: Optional[str] = None) -> int:
        """
        获取下载记录总数
        """
        query = db.query(self.model)
        if space_id is not None:
            query = query.filter(DownloadRecord.space_id == space_id)
        return query.count()


# 创建CRUD实例
crud_download_record = CRUDDownloadRecord(DownloadRecord)