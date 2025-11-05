from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, db: Session, *, username_or_email: str) -> Optional[User]:
        """
        根据用户名或邮箱获取用户
        """
        return db.query(User).filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        创建用户
        """
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        更新用户信息
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        验证用户凭据
        """
        user = self.get_by_username_or_email(db, username_or_email=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        检查用户是否活跃
        """
        return user.is_active

    def is_admin(self, user: User) -> bool:
        """
        检查用户是否为管理员
        """
        return user.role == "admin"

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        获取用户列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        """
        获取用户总数
        """
        return db.query(self.model).count()


# 创建CRUD实例
crud_user = CRUDUser(User)