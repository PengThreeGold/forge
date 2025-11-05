from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api.deps import get_current_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.core.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_current_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录获取访问令牌
    """
    user = crud.user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(
    refresh_data: schemas.TokenRefresh,
    db: Session = Depends(get_current_db)
) -> Any:
    """
    使用刷新令牌获取新的访问令牌
    """
    user_id = verify_token(refresh_data.refresh_token, "refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.user.get(db, id=user_id)
    if not user or not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/profile", response_model=schemas.User)
def read_current_user(
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.put("/admin/password", response_model=schemas.ResponseModel)
def change_password(
    password_data: schemas.PasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
) -> Any:
    """
    修改当前用户密码
    """
    # 验证原密码
    user = crud.user.authenticate(
        db, username=current_user.username, password=password_data.old_password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 更新密码
    user_in = schemas.UserUpdate(password=password_data.new_password)
    crud.user.update(db, db_obj=current_user, obj_in=user_in)
    
    return schemas.ResponseModel(success=True, message="密码修改成功")


@router.post("/admin/init", response_model=schemas.ResponseModel)
def init_admin(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_current_db)
) -> Any:
    """
    初始化管理员账户（仅当没有管理员时可用）
    """
    # 检查是否已有管理员
    existing_admin = db.query(models.User).filter(
        models.User.role == "admin"
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统已存在管理员账户"
        )
    
    # 检查用户名是否已存在
    existing_user = crud.user.get_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建管理员用户
    user_in = schemas.UserCreate(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role="admin"
    )
    
    crud.user.create(db, obj_in=user_in)
    
    return schemas.ResponseModel(success=True, message="管理员账户创建成功")