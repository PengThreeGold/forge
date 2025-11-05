from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.deps import get_current_db
from app.core.deps import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=schemas.PaginatedResponse[schemas.User])
def read_users(
    db: Session = Depends(get_current_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_admin_user)
) -> Any:
    """
    获取用户列表（管理员权限）
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    total = crud.user.count(db)
    
    return schemas.PaginatedResponse(
        items=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=schemas.ResponseModel[schemas.User])
def create_user(
    *,
    db: Session = Depends(get_current_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(get_current_admin_user)
) -> Any:
    """
    创建新用户（管理员权限）
    """
    # 检查用户名是否已存在
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_in.email:
        user = crud.user.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    user = crud.user.create(db, obj_in=user_in)
    return schemas.ResponseModel(
        success=True,
        message="用户创建成功",
        data=user
    )


@router.get("/{user_id}", response_model=schemas.ResponseModel[schemas.User])
def read_user(
    user_id: int,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_admin_user)
) -> Any:
    """
    获取用户详情（管理员权限）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return schemas.ResponseModel(
        success=True,
        message="获取用户详情成功",
        data=user
    )


@router.put("/{user_id}", response_model=schemas.ResponseModel[schemas.User])
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_admin_user)
) -> Any:
    """
    更新用户信息（管理员权限）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果更新用户名，检查是否已存在
    if user_in.username and user_in.username != user.username:
        existing_user = crud.user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 如果更新邮箱，检查是否已存在
    if user_in.email and user_in.email != user.email:
        existing_user = crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return schemas.ResponseModel(
        success=True,
        message="用户信息更新成功",
        data=user
    )


@router.delete("/{user_id}", response_model=schemas.ResponseModel)
def delete_user(
    user_id: int,
    db: Session = Depends(get_current_db),
    current_user: models.User = Depends(get_current_admin_user)
) -> Any:
    """
    删除用户（管理员权限）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    crud.user.remove(db, id=user_id)
    return schemas.ResponseModel(
        success=True,
        message="用户删除成功",
        data=None
    )