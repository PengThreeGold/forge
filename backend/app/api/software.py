import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response, admin_required
from app.utils.file import save_file, move_file_to_storage, delete_file, get_file_size_human_readable
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord
from app import db
from flask_sqlalchemy import SQLAlchemy

# 类型提示，避免pylance错误
from typing import Any, cast
session: Any = db.session

software_bp = Blueprint('software', __name__)


@software_bp.route('/software', methods=['GET'])
@jwt_required()
@admin_required
def get_spaces():
    """获取软件空间列表"""
    spaces = SoftwareSpace.query.order_by(SoftwareSpace.created_at.desc()).all()
    spaces_data = [space.to_dict() for space in spaces]
    
    return success_response(spaces_data)


@software_bp.route('/software', methods=['POST'])
@jwt_required()
@admin_required
def create_space():
    """创建软件空间"""
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    name = data.get('name')
    description = data.get('description')
    author = data.get('author')
    webhook_url = data.get('webhook_url')
    
    if not name:
        return error_response("软件名称不能为空", 400)
    
    current_user_id = get_jwt_identity()
    
    # 检查名称是否已存在
    existing_space = SoftwareSpace.query.filter_by(name=name).first()
    if existing_space:
        return error_response("软件名称已存在", 400)
    
    # 创建软件空间
    space = SoftwareSpace(
        name=name,
        description=description,
        author=author,
        webhook_url=webhook_url,
        created_by=current_user_id
    )
    
    session.add(space)
    session.commit()
    
    return success_response(space.to_dict(include_api_key=True), "软件空间创建成功")


@software_bp.route('/software/<int:space_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_space(space_id):
    """获取软件空间详情"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    return success_response(space.to_dict(include_api_key=True))


@software_bp.route('/software/<int:space_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_space(space_id):
    """更新软件空间"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    # 更新字段
    if 'name' in data:
        # 检查名称是否已存在（排除当前空间）
        existing_space = SoftwareSpace.query.filter(
            SoftwareSpace.name == data['name'],
            SoftwareSpace.id != space_id
        ).first()
        
        if existing_space:
            return error_response("软件名称已存在", 400)
        
        space.name = data['name']
    
    if 'description' in data:
        space.description = data['description']
    
    if 'author' in data:
        space.author = data['author']
    
    if 'webhook_url' in data:
        space.webhook_url = data['webhook_url']
    
    session.commit()
    
    return success_response(space.to_dict(include_api_key=True), "软件空间更新成功")


@software_bp.route('/software/<int:space_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_space(space_id):
    """删除软件空间"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    # 删除相关文件
    for version in space.versions:
        if os.path.exists(version.file_path):
            delete_file(version.file_path)
    
    session.delete(space)
    session.commit()
    
    return success_response(message="软件空间删除成功")


@software_bp.route('/software/<int:space_id>/regenerate-api-key', methods=['POST'])
@jwt_required()
@admin_required
def regenerate_api_key(space_id):
    """重新生成API密钥"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    new_api_key = space.regenerate_api_key()
    session.commit()
    
    return success_response({'api_key': new_api_key}, "API密钥重新生成成功")


@software_bp.route('/software/<int:space_id>/versions', methods=['GET'])
@jwt_required()
@admin_required
def get_versions(space_id):
    """获取软件版本列表"""
    space = SoftwareSpace.query.get_or_404(space_id)
    versions = space.versions.order_by(SoftwareVersion.created_at.desc()).all()
    
    versions_data = []
    for version in versions:
        version_dict = version.to_dict(include_file_path=True)
        version_dict['file_size_human'] = get_file_size_human_readable(version.file_size or 0)
        versions_data.append(version_dict)
    
    return success_response(versions_data)


@software_bp.route('/software/<int:space_id>/versions', methods=['POST'])
@jwt_required()
@admin_required
def create_version(space_id):
    """创建软件版本"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return error_response("没有上传文件", 400)
    
    file = request.files['file']
    if file.filename == '':
        return error_response("没有选择文件", 400)
    
    # 获取其他参数
    version = request.form.get('version')
    release_note = request.form.get('release_note')
    documentation_url = request.form.get('documentation_url')
    
    if not version:
        return error_response("版本号不能为空", 400)
    
    # 检查版本是否已存在
    existing_version = SoftwareVersion.query.filter_by(
        space_id=space_id,
        version=version
    ).first()
    
    if existing_version:
        return error_response(f"版本 {version} 已存在", 400)
    
    current_user_id = get_jwt_identity()
    
    # 保存文件
    file_info, message = save_file(file)
    if not file_info:
        return error_response(message, 400)
    
    # 将文件移动到软件存储目录
    file_path, message = move_file_to_storage(
        file_info['file_path'],
        space_id,
        version
    )
    
    if not file_path:
        return error_response(message, 500)
    
    # 创建软件版本
    software_version = SoftwareVersion(
        space_id=space_id,
        version=version,
        file_path=file_path,
        file_size=file_info['file_size'],
        file_hash=file_info['file_hash'],
        release_note=release_note,
        documentation_url=documentation_url,
        created_by=current_user_id
    )
    
    session.add(software_version)
    session.commit()
    
    version_data = software_version.to_dict(include_file_path=True)
    version_data['file_size_human'] = get_file_size_human_readable(software_version.file_size or 0)
    
    return success_response(version_data, "软件版本创建成功")


@software_bp.route('/versions/<int:version_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_version(version_id):
    """获取软件版本详情"""
    version = SoftwareVersion.query.get_or_404(version_id)
    
    version_data = version.to_dict(include_file_path=True)
    version_data['file_size_human'] = get_file_size_human_readable(version.file_size or 0)
    
    return success_response(version_data)


@software_bp.route('/versions/<int:version_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_version(version_id):
    """更新软件版本"""
    version = SoftwareVersion.query.get_or_404(version_id)
    
    data = request.get_json()
    
    if not data:
        return error_response("请求参数不能为空", 400)
    
    # 更新字段
    if 'release_note' in data:
        version.release_note = data['release_note']
    
    if 'documentation_url' in data:
        version.documentation_url = data['documentation_url']
    
    session.commit()
    
    version_data = version.to_dict(include_file_path=True)
    version_data['file_size_human'] = get_file_size_human_readable(version.file_size or 0)
    
    return success_response(version_data, "软件版本更新成功")


@software_bp.route('/versions/<int:version_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_version(version_id):
    """删除软件版本"""
    version = SoftwareVersion.query.get_or_404(version_id)
    
    # 删除文件
    if os.path.exists(version.file_path):
        delete_file(version.file_path)
    
    session.delete(version)
    session.commit()
    
    return success_response(message="软件版本删除成功")


@software_bp.route('/versions/<int:version_id>/publish', methods=['PUT'])
@jwt_required()
@admin_required
def publish_version(version_id):
    """发布/下架软件版本"""
    version = SoftwareVersion.query.get_or_404(version_id)
    
    data = request.get_json()
    
    if not data or 'publish' not in data:
        return error_response("请求参数不能为空", 400)
    
    publish = data['publish']
    
    if publish:
        version.publish()
        message = "软件版本发布成功"
    else:
        version.unpublish()
        message = "软件版本下架成功"
    
    session.commit()
    
    version_data = version.to_dict(include_file_path=True)
    version_data['file_size_human'] = get_file_size_human_readable(version.file_size or 0)
    
    return success_response(version_data, message)


@software_bp.route('/download/<int:version_id>', methods=['GET'])
@jwt_required()
@admin_required
def download_version(version_id):
    """下载软件版本（管理员）"""
    version = SoftwareVersion.query.get_or_404(version_id)
    
    if not os.path.exists(version.file_path):
        return error_response("文件不存在", 404)
    
    # 记录下载
    record = DownloadRecord(
        version_id=version.id,
        space_id=version.space_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    session.add(record)
    session.commit()
    
    # 发送文件
    return send_file(
        version.file_path,
        as_attachment=True,
        download_name=os.path.basename(version.file_path)
    )


# 公开API接口
@software_bp.route('/public/spaces', methods=['GET'])
def get_public_spaces():
    """获取所有公开的软件空间列表（公开API）"""
    # 获取所有有已发布版本的软件空间
    spaces = SoftwareSpace.query.join(
        SoftwareVersion,
        SoftwareSpace.id == SoftwareVersion.space_id
    ).filter(
        SoftwareVersion.is_published == True
    ).distinct().order_by(SoftwareSpace.created_at.desc()).all()
    
    spaces_data = []
    for space in spaces:
        space_dict = space.to_dict()
        space_dict.pop('api_key', None)  # 不返回API密钥
        
        # 添加已发布版本计数
        published_versions_count = SoftwareVersion.query.filter_by(
            space_id=space.id,
            is_published=True
        ).count()
        space_dict['versions_count'] = published_versions_count
        
        # 获取最新发布的版本
        latest_version = SoftwareVersion.query.filter_by(
            space_id=space.id,
            is_published=True
        ).order_by(SoftwareVersion.created_at.desc()).first()
        
        if latest_version:
            space_dict['latest_version'] = latest_version.version
            space_dict['latest_publish_date'] = latest_version.publish_date.isoformat() if latest_version.publish_date else None
        
        spaces_data.append(space_dict)
    
    return success_response(spaces_data)


@software_bp.route('/public/space/<int:space_id>', methods=['GET'])
def get_space_info_by_id(space_id):
    """通过ID获取软件空间信息（公开API）"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    # 检查是否有已发布的版本
    has_published_versions = SoftwareVersion.query.filter_by(
        space_id=space_id,
        is_published=True
    ).first() is not None
    
    if not has_published_versions:
        return error_response("该软件空间没有已发布的版本", 404)
    
    space_data = space.to_dict()
    space_data.pop('api_key', None)  # 不返回API密钥
    
    # 获取最新发布的版本
    latest_version = SoftwareVersion.query.filter_by(
        space_id=space_id,
        is_published=True
    ).order_by(SoftwareVersion.created_at.desc()).first()
    
    if latest_version:
        space_data['latest_version'] = latest_version.version
        space_data['latest_publish_date'] = latest_version.publish_date.isoformat() if latest_version.publish_date else None
    
    return success_response(space_data)


@software_bp.route('/public/<api_key>', methods=['GET'])
def get_space_info(api_key):
    """获取软件空间信息（公开API）"""
    space = SoftwareSpace.query.filter_by(api_key=api_key).first()
    
    if not space:
        return error_response("API密钥无效", 404)
    
    space_data = space.to_dict()
    space_data.pop('api_key', None)  # 不返回API密钥
    
    return success_response(space_data)


@software_bp.route('/public/<api_key>/versions', methods=['GET'])
def get_versions_info(api_key):
    """获取软件版本列表（公开API）"""
    space = SoftwareSpace.query.filter_by(api_key=api_key).first()
    
    if not space:
        return error_response("API密钥无效", 404)
    
    # 只返回已发布的版本
    versions = space.versions.filter_by(is_published=True).order_by(SoftwareVersion.created_at.desc()).all()
    
    versions_data = []
    for version in versions:
        version_dict = version.to_dict()
        version_dict['file_size_human'] = get_file_size_human_readable(version.file_size or 0)
        versions_data.append(version_dict)
    
    return success_response(versions_data)


@software_bp.route('/public/<api_key>/download/<string:version>', methods=['GET'])
def download_version_public(api_key, version):
    """下载软件版本（公开API）"""
    space = SoftwareSpace.query.filter_by(api_key=api_key).first()
    
    if not space:
        return error_response("API密钥无效", 404)
    
    # 查找指定版本
    if version.lower() == 'latest':
        software_version = space.get_latest_version()
        if not software_version:
            return error_response("没有可用的版本", 404)
    else:
        software_version = SoftwareVersion.query.filter_by(
            space_id=space.id,
            version=version,
            is_published=True
        ).first()
    
    if not software_version:
        return error_response("版本不存在或未发布", 404)
    
    if not os.path.exists(software_version.file_path):
        return error_response("文件不存在", 404)
    
    # 记录下载
    record = DownloadRecord(
        version_id=software_version.id,
        space_id=space.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    session.add(record)
    session.commit()
    
    # 发送文件
    return send_file(
        software_version.file_path,
        as_attachment=True,
        download_name=os.path.basename(software_version.file_path)
    )