from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class SoftwareArchitectureFile(Base):
    __tablename__ = "software_architecture_files"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("software_versions.id"), nullable=False, index=True)
    architecture = Column(String(20), nullable=False, index=True)  # x86, x64, arm64, arm, universal
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # MD5 hash
    download_count = Column(Integer, default=0, nullable=False)

    # 关系
    version = relationship("SoftwareVersion", back_populates="architecture_files", cascade="save-update, merge")
    download_records = relationship("DownloadRecord", back_populates="architecture_file", cascade="all, delete-orphan")