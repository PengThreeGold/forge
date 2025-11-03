import os
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord
from app.utils.file import save_file, move_file_to_storage, delete_file, get_file_size_human_readable
from app import db
from app.api.webhook import handle_download_event, handle_version_publish_event


class SoftwareService:
    """软件服务类"""
    
    @staticmethod
    def create_space(name, description=None, author=None, webhook_url=None, created_by=None):
        """创建软件空间"""
        # 检查名称是否已存在
        existing_space = SoftwareSpace.query.filter_by(name=name).first()
        if existing_space:
            return None, "软件名称已存在"
        
        # 创建软件空间
        space = SoftwareSpace(
            name=name,
            description=description,
            author=author,
            webhook_url=webhook_url,
            created_by=created_by
        )
        
        db.session.add(space)
        db.session.commit()
        
        return space, "软件空间创建成功"
    
    @staticmethod
    def get_space(space_id):
        """获取软件空间"""
        return SoftwareSpace.query.get(space_id)
    
    @staticmethod
    def get_all_spaces():
        """获取所有软件空间"""
        return SoftwareSpace.query.order_by(SoftwareSpace.created_at.desc()).all()
    
    @staticmethod
    def update_space(space_id, name=None, description=None, author=None, webhook_url=None):
        """更新软件空间"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return None, "软件空间不存在"
        
        # 更新字段
        if name and name != space.name:
            # 检查名称是否已存在
            existing_space = SoftwareSpace.query.filter(
                SoftwareSpace.name == name,
                SoftwareSpace.id != space_id
            ).first()
            
            if existing_space:
                return None, "软件名称已存在"
            
            space.name = name
        
        if description is not None:
            space.description = description
        
        if author is not None:
            space.author = author
        
        if webhook_url is not None:
            space.webhook_url = webhook_url
        
        db.session.commit()
        
        return space, "软件空间更新成功"
    
    @staticmethod
    def delete_space(space_id):
        """删除软件空间"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return False, "软件空间不存在"
        
        # 删除相关文件
        for version in space.versions:
            if os.path.exists(version.file_path):
                delete_file(version.file_path)
        
        db.session.delete(space)
        db.session.commit()
        
        return True, "软件空间删除成功"
    
    @staticmethod
    def regenerate_api_key(space_id):
        """重新生成API密钥"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return None, "软件空间不存在"
        
        new_api_key = space.regenerate_api_key()
        db.session.commit()
        
        return new_api_key, "API密钥重新生成成功"
    
    @staticmethod
    def create_version(space_id, version, file, release_note=None, documentation_url=None, created_by=None):
        """创建软件版本"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return None, "软件空间不存在"
        
        # 检查版本是否已存在
        existing_version = SoftwareVersion.query.filter_by(
            space_id=space_id,
            version=version
        ).first()
        
        if existing_version:
            return None, f"版本 {version} 已存在"
        
        # 保存文件
        file_info, message = save_file(file)
        if not file_info:
            return None, message
        
        # 将文件移动到软件存储目录
        file_path, message = move_file_to_storage(
            file_info['file_path'],
            space_id,
            version
        )
        
        if not file_path:
            return None, message
        
        # 创建软件版本
        software_version = SoftwareVersion(
            space_id=space_id,
            version=version,
            file_path=file_path,
            file_size=file_info['file_size'],
            file_hash=file_info['file_hash'],
            release_note=release_note,
            documentation_url=documentation_url,
            created_by=created_by
        )
        
        db.session.add(software_version)
        db.session.commit()
        
        return software_version, "软件版本创建成功"
    
    @staticmethod
    def get_version(version_id):
        """获取软件版本"""
        return SoftwareVersion.query.get(version_id)
    
    @staticmethod
    def get_versions_by_space(space_id):
        """获取指定软件空间的所有版本"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return [], "软件空间不存在"
        
        return space.versions.order_by(SoftwareVersion.created_at.desc()).all(), "获取成功"
    
    @staticmethod
    def update_version(version_id, release_note=None, documentation_url=None):
        """更新软件版本"""
        version = SoftwareVersion.query.get(version_id)
        
        if not version:
            return None, "软件版本不存在"
        
        # 更新字段
        if release_note is not None:
            version.release_note = release_note
        
        if documentation_url is not None:
            version.documentation_url = documentation_url
        
        db.session.commit()
        
        return version, "软件版本更新成功"
    
    @staticmethod
    def delete_version(version_id):
        """删除软件版本"""
        version = SoftwareVersion.query.get(version_id)
        
        if not version:
            return False, "软件版本不存在"
        
        # 删除文件
        if os.path.exists(version.file_path):
            delete_file(version.file_path)
        
        db.session.delete(version)
        db.session.commit()
        
        return True, "软件版本删除成功"
    
    @staticmethod
    def publish_version(version_id, publish=True):
        """发布/下架软件版本"""
        version = SoftwareVersion.query.get(version_id)
        
        if not version:
            return None, "软件版本不存在"
        
        if publish:
            version.publish()
            message = "软件版本发布成功"
        else:
            version.unpublish()
            message = "软件版本下架成功"
        
        db.session.commit()
        
        # 触发版本发布事件
        if publish:
            handle_version_publish_event(version)
        
        return version, message
    
    @staticmethod
    def download_version(version_id, ip_address, user_agent=None):
        """下载软件版本"""
        version = SoftwareVersion.query.get(version_id)
        
        if not version:
            return None, "软件版本不存在"
        
        if not version.is_published:
            return None, "软件版本未发布"
        
        if not os.path.exists(version.file_path):
            return None, "文件不存在"
        
        # 记录下载
        record = DownloadRecord(
            version_id=version.id,
            space_id=version.space_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(record)
        db.session.commit()
        
        # 触发下载事件
        handle_download_event(record)
        
        return version.file_path, "下载成功"
    
    @staticmethod
    def get_latest_version(space_id):
        """获取最新版本"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return None, "软件空间不存在"
        
        return space.get_latest_version()
    
    @staticmethod
    def get_space_by_api_key(api_key):
        """根据API密钥获取软件空间"""
        return SoftwareSpace.query.filter_by(api_key=api_key).first()
    
    @staticmethod
    def get_version_by_space_and_version(space_id, version):
        """根据软件空间和版本号获取版本"""
        return SoftwareVersion.query.filter_by(
            space_id=space_id,
            version=version
        ).first()