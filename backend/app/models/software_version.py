from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SoftwareVersion(Base):
    __tablename__ = "software_versions"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(String(8), ForeignKey("software_spaces.id"), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    release_note = Column(Text, nullable=True)
    documentation_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
    publish_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    space = relationship("SoftwareSpace", back_populates="versions")
    creator = relationship("User", back_populates="created_versions")
    download_records = relationship("DownloadRecord", back_populates="version")