import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response, admin_required
from app.models.user import User
from app import db
from typing import Any

# 类型提示，避免pylance错误
session: Any = db.session

user_management_bp = Blueprint('user_management', __name__)


@user_management_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    username = request.args.get('username', type=str)
    
    # 构建查询
    query = User.query
    
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    
    # 分页查询
    pagination = query.order_by(
        User.created_at.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 格式化结果
    users_data = [user.to_dict() for user in pagination.items]
    
    return success_response({
        'users': users_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@user_management_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """创建用户"""
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')
    
    if not username or not password or not role:
        return error_response("用户名、密码和角色不能为空", 400)
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return error_response("用户名已存在", 409)
    
    # 创建新用户
    user = User(username, password, email, role)
    
    session.add(user)
    session.commit()
    
    return success_response({
        'user': user.to_dict()
    }, "用户创建成功")


@user_management_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    
    return success_response({
        'user': user.to_dict()
    })


@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    # 更新字段
    if 'username' in data:
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter(
            User.username == data['username'],
            User.id != user_id
        ).first()
        
        if existing_user:
            return error_response("用户名已存在", 400)
        
        user.username = data['username']
    
    if 'email' in data:
        user.email = data['email']
    
    if 'role' in data:
        user.role = data['role']
    
    # 如果提供了新密码，则更新密码
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    session.commit()
    
    return success_response({
        'user': user.to_dict()
    }, "用户信息更新成功")


@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 检查是否为当前登录用户
    current_user_id = get_jwt_identity()
    if user_id == current_user_id:
        return error_response("不能删除当前登录用户", 400)
    
    session.delete(user)
    session.commit()
    
    return success_response(message="用户删除成功")