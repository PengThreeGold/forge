from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(String(8), ForeignKey("software_spaces.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    webhook_url = Column(String(500), nullable=False)
    payload = Column(Text, nullable=True)  # JSON格式的请求数据
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    attempt_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    space = relationship("SoftwareSpace", back_populates="webhook_logs")