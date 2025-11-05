import os
import json
import platform
import psutil
import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response, admin_required
from app import db
from typing import Any

# 类型提示，避免pylance错误
session: Any = db.session

system_bp = Blueprint('system', __name__)


@system_bp.route('/system/info', methods=['GET'])
@jwt_required()
@admin_required
def get_system_info():
    """获取系统信息"""
    try:
        # 获取系统基本信息
        system_info = {
            'version': '1.0.0',  # 可以从配置文件或环境变量获取
            'uptime': get_uptime(),
            'storage': get_storage_info(),
            'database': get_database_info()
        }
        
        return success_response({
            'system': system_info
        }, "获取系统信息成功")
    
    except Exception as e:
        return error_response(f"获取系统信息失败: {str(e)}", 500)


@system_bp.route('/system/backup', methods=['POST'])
@jwt_required()
@admin_required
def create_backup():
    """创建系统备份"""
    try:
        # 生成备份ID（使用时间戳）
        backup_id = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建备份目录
        backup_dir = os.path.join(current_app.config.get('BACKUP_FOLDER', 'backups'))
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份文件路径
        backup_file_path = os.path.join(backup_dir, f"{backup_id}.json")
        
        # 获取备份数据
        from app.models.user import User
        backup_data = {
            'backup_info': {
                'id': backup_id,
                'created_at': datetime.datetime.utcnow().isoformat(),
                'version': '1.0.0'
            },
            'users': [user.to_dict() for user in User.query.all()],
            'software_spaces': [],
            'software_versions': [],
            'download_records': [],
            'webhook_logs': []
        }
        
        # 保存备份文件
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # 获取文件大小
        file_size = os.path.getsize(backup_file_path)
        
        return success_response({
            'backup_id': backup_id,
            'download_url': f'/api/system/backup/download/{backup_id}',
            'size': file_size
        }, "系统备份创建成功")
    
    except Exception as e:
        return error_response(f"创建系统备份失败: {str(e)}", 500)


@system_bp.route('/system/backup/download/<backup_id>', methods=['GET'])
@jwt_required()
@admin_required
def download_backup(backup_id):
    """下载备份文件"""
    try:
        # 备份目录
        backup_dir = current_app.config.get('BACKUP_FOLDER', 'backups')
        backup_file_path = os.path.join(backup_dir, f"{backup_id}.json")
        
        if not os.path.exists(backup_file_path):
            return error_response("备份文件不存在", 404)
        
        return send_file(
            backup_file_path,
            as_attachment=True,
            download_name=f"{backup_id}.json"
        )
    
    except Exception as e:
        return error_response(f"下载备份文件失败: {str(e)}", 500)


def get_uptime():
    """获取系统运行时间"""
    try:
        # 获取系统启动时间
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        # 计算运行时间
        uptime = datetime.datetime.now() - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{days} days, {hours}:{minutes:02d}"
    except:
        return "未知"


def get_storage_info():
    """获取存储信息"""
    try:
        # 获取根目录的磁盘使用情况
        disk_usage = psutil.disk_usage('/')
        
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'available': disk_usage.free
        }
    except:
        # 如果psutil不可用，尝试使用os.statvfs
        try:
            # 在Windows系统上不使用statvfs
            if hasattr(os, 'statvfs'):
                statvfs = os.statvfs('/')
            else:
                # Windows系统使用其他方法获取磁盘信息
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p('C:/'), ctypes.byref(free_bytes),
                    ctypes.byref(total_bytes), None
                )
                total = total_bytes.value
                available = free_bytes.value
                used = total - available
            total = statvfs.f_frsize * statvfs.f_blocks
            available = statvfs.f_frsize * statvfs.f_bavail
            used = total - available
        except:
            return {
                'total': 0,
                'used': 0,
                'available': 0
            }


def get_database_info():
    """获取数据库信息"""
    try:
        # 获取数据库类型
        db_type = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('://')[0]
        
        # 获取数据库大小（SQLite）
        if 'sqlite' in db_type.lower():
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                return {
                    'type': 'SQLite',
                    'version': '未知',
                    'size': size
                }
        
        # 其他数据库类型的处理
        return {
            'type': db_type,
            'version': '未知',
            'size': 0
        }
    except:
        return {
            'type': '未知',
            'version': '未知',
            'size': 0
        }