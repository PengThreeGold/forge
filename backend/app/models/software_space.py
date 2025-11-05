from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SoftwareSpace(Base):
    __tablename__ = "software_spaces"

    id = Column(String(8), primary_key=True, index=True)  # 8位随机字符
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    api_key = Column(String(60), unique=True, index=True, nullable=False)
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(60), nullable=True)
    webhook_events = Column(Text, nullable=True)  # JSON格式存储事件列表
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    creator = relationship("User", back_populates="created_spaces")
    versions = relationship("SoftwareVersion", back_populates="space", cascade="all, delete-orphan")
    download_records = relationship("DownloadRecord", back_populates="space")
    webhook_logs = relationship("WebhookLog", back_populates="space")