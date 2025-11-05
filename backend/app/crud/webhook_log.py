from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.webhook_log import WebhookLog


class CRUDWebhookLog(CRUDBase[WebhookLog, dict, dict]):
    def create(
        self,
        db: Session,
        *,
        space_id: str,
        event_type: str,
        webhook_url: str,
        payload: Optional[str] = None,
        response_status: Optional[int] = None,
        response_body: Optional[str] = None
    ) -> WebhookLog:
        """
        创建Webhook日志
        """
        db_obj = WebhookLog(
            space_id=space_id,
            event_type=event_type,
            webhook_url=webhook_url,
            payload=payload,
            response_status=response_status,
            response_body=response_body,
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
    ) -> List[WebhookLog]:
        """
        根据软件空间ID获取Webhook日志
        """
        return (
            db.query(self.model)
            .filter(WebhookLog.space_id == space_id)
            .order_by(desc(WebhookLog.attempt_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_event_type(
        self,
        db: Session,
        *,
        event_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebhookLog]:
        """
        根据事件类型获取Webhook日志
        """
        return (
            db.query(self.model)
            .filter(WebhookLog.event_type == event_type)
            .order_by(desc(WebhookLog.attempt_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_failed_logs(
        self,
        db: Session,
        *,
        space_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebhookLog]:
        """
        获取失败的Webhook日志
        """
        query = db.query(self.model).filter(
            WebhookLog.response_status >= 400
        )
        
        if space_id is not None:
            query = query.filter(WebhookLog.space_id == space_id)
        
        return (
            query.order_by(desc(WebhookLog.attempt_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, db: Session, space_id: Optional[str] = None) -> int:
        """
        获取Webhook日志总数
        """
        query = db.query(self.model)
        if space_id is not None:
            query = query.filter(WebhookLog.space_id == space_id)
        return query.count()


# 创建CRUD实例
crud_webhook_log = CRUDWebhookLog(WebhookLog)