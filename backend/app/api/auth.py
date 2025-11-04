import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response, admin_required
from app.utils.auth import authenticate_user, create_user, change_password
from typing import Any
from app import db

# 类型提示，避免 pylance 错误
session: Any = db.session

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """管理员登录"""
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error_response("用户名和密码不能为空", 400)
    
    user = authenticate_user(username, password)
    
    if not user:
        return error_response("用户名或密码错误", 401)
    
    if user.role != 'admin':
        return error_response("权限不足", 403)
    
    # 创建访问令牌和刷新令牌
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return success_response({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }, "登录成功")


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新令牌"""
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    
    return success_response({
        'access_token': new_token
    }, "令牌刷新成功")


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """管理员登出"""
    return success_response(message="登出成功")


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@admin_required
def get_profile():
    """获取当前用户信息"""
    from app.models.user import User
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response("用户不存在", 404)
    
    return success_response(user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@admin_required
def change_password_route():
    """修改密码"""
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return error_response("原密码和新密码不能为空", 400)
    
    current_user_id = get_jwt_identity()
    success, message = change_password(current_user_id, old_password, new_password)
    
    if success:
        return success_response(message=message)
    else:
        return error_response(message, 400)


@auth_bp.route('/init-admin', methods=['POST'])
def init_admin():
    """初始化管理员账户（仅在安装时使用）"""
    # 检查是否已经存在管理员
    from app.models.user import User
    from app import db
    
    admin_exists = User.query.filter_by(role='admin').first()
    
    if admin_exists:
        return error_response("管理员已存在，无法重复创建", 400)
    
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return error_response("用户名和密码不能为空", 400)
    
    user, message = create_user(username, password, email, 'admin')
    
    if user:
        return success_response({
            'user': user.to_dict()
        }, message)
    else:
        return error_response(message, 400)


@auth_bp.route('/init-admin', methods=['GET'])
def init_admin_status():
    """检查是否需要初始化管理员账户（不创建）

    返回：
    - 如果管理员已存在：{ init_required: False }
    - 如果管理员不存在：{ init_required: True }
    这样前端可以用GET请求检测是否需要初始化，而不会误触发创建操作。
    """
    try:
        from app.models.user import User

        admin_exists = User.query.filter_by(role='admin').first() is not None

        return success_response({'init_required': not admin_exists})
    except Exception as e:
        # 返回更详细的错误信息以便调试（生产环境可以改为更模糊的消息）
        return error_response(f"检查初始化状态失败: {str(e)}", 500)