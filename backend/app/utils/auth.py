from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, decode_token
from app.models.user import User
from typing import Any
from app import db

# 类型提示，避免pylance错误
session: Any = db.session


def generate_token(user_id, expires_in=3600):
    """生成JWT令牌"""
    return create_access_token(
        identity=user_id,
        expires_delta=timedelta(seconds=expires_in)
    )


def verify_token(token):
    """验证JWT令牌"""
    try:
        decoded_token = decode_token(token)
        return decoded_token['sub']
    except Exception:
        return None  # 令牌无效或已过期


def authenticate_user(username, password):
    """验证用户身份"""
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        return user
    
    return None


def create_user(username, password, email=None, role='admin'):
    """创建新用户"""
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return None, "用户名已存在"
    
    # 创建新用户
    user = User(
        username=username,
        password=password,
        email=email,
        role=role
    )
    
    from app import db
    session.add(user)
    session.commit()
    
    return user, "用户创建成功"


def change_password(user_id, old_password, new_password):
    """修改用户密码"""
    user = User.query.get(user_id)
    
    if not user:
        return False, "用户不存在"
    
    if not user.check_password(old_password):
        return False, "原密码错误"
    
    user.set_password(new_password)
    
    from app import db
    session.commit()
    
    return True, "密码修改成功"