from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class DownloadRecord(Base):
    __tablename__ = "download_records"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(String(8), ForeignKey("software_spaces.id"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("software_versions.id"), nullable=False, index=True)
    architecture_file_id = Column(Integer, ForeignKey("software_architecture_files.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # 支持IPv6
    user_agent = Column(String(500), nullable=True)
    referer = Column(String(500), nullable=True)
    download_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    space = relationship("SoftwareSpace", back_populates="download_records")
    version = relationship("SoftwareVersion", back_populates="download_records")
    architecture_file = relationship("SoftwareArchitectureFile", back_populates="download_records")