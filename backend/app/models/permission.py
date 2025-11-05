from sqlalchemy import Column, String

from app.db.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(50), primary_key=True, index=True)  # 如: software:create
    name = Column(String(100), nullable=False)  # 如: 创建软件
    description = Column(String(500), nullable=True)  # 如: 创建和管理软件空间
    category = Column(String(50), nullable=False, index=True)  # 如: 软件管理