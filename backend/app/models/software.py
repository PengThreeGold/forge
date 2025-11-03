import os
import secrets
import hashlib
from datetime import datetime
from flask import current_app
from app import db


class SoftwareSpace(db.Model):
    """软件空间模型"""
    __tablename__ = 'software_spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(50), nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    webhook_url = db.Column(db.String(255), nullable=True)
    webhook_secret = db.Column(db.String(64), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    versions = db.relationship('SoftwareVersion', backref='space', lazy='dynamic', cascade='all, delete-orphan')
    download_records = db.relationship('DownloadRecord', backref='space', lazy='dynamic')
    webhook_logs = db.relationship('WebhookLog', backref='space', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, name, description=None, author=None, webhook_url=None, created_by=None):
        self.name = name
        self.description = description
        self.author = author
        self.webhook_url = webhook_url
        self.api_key = self._generate_api_key()
        self.created_by = created_by
    
    def _generate_api_key(self):
        """生成API密钥"""
        return secrets.token_hex(32)
    
    def regenerate_api_key(self):
        """重新生成API密钥"""
        self.api_key = self._generate_api_key()
        return self.api_key
    
    def get_latest_version(self):
        """获取最新版本"""
        return self.versions.order_by(SoftwareVersion.created_at.desc()).first()
    
    def to_dict(self, include_api_key=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'webhook_url': self.webhook_url,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'versions_count': self.versions.count(),
            'downloads_count': self.download_records.count()
        }
        
        if include_api_key:
            result['api_key'] = self.api_key
            
        return result
    
    def __repr__(self):
        return f'<SoftwareSpace {self.name}>'


class SoftwareVersion(db.Model):
    """软件版本模型"""
    __tablename__ = 'software_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('software_spaces.id'), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_hash = db.Column(db.String(64), nullable=True)
    release_note = db.Column(db.Text, nullable=True)
    documentation_url = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    publish_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    download_records = db.relationship('DownloadRecord', backref='version', lazy='dynamic')
    
    def __init__(self, space_id, version, file_path, file_size=None, file_hash=None, 
                 release_note=None, documentation_url=None, created_by=None):
        self.space_id = space_id
        self.version = version
        self.file_path = file_path
        self.file_size = file_size
        self.file_hash = file_hash
        self.release_note = release_note
        self.documentation_url = documentation_url
        self.created_by = created_by
    
    def calculate_file_hash(self, file_path=None):
        """计算文件哈希值"""
        path = file_path or self.file_path
        if not path or not os.path.exists(path):
            return None
            
        sha256_hash = hashlib.sha256()
        with open(path, 'rb') as f:
            while True:
                byte_block = f.read(4096)
                if not byte_block:
                    break
                sha256_hash.update(byte_block)
        
        self.file_hash = sha256_hash.hexdigest()
        return self.file_hash
    
    def publish(self):
        """发布版本"""
        self.is_published = True
        self.publish_date = datetime.utcnow()
        return self.is_published
    
    def unpublish(self):
        """取消发布版本"""
        self.is_published = False
        self.publish_date = None
        return self.is_published
    
    def get_download_count(self):
        """获取下载次数"""
        return self.download_records.count()
    
    def to_dict(self, include_file_path=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'space_id': self.space_id,
            'version': self.version,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'release_note': self.release_note,
            'documentation_url': self.documentation_url,
            'is_published': self.is_published,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'download_count': self.get_download_count()
        }
        
        if include_file_path:
            result['file_path'] = self.file_path
            
        return result
    
    def __repr__(self):
        return f'<SoftwareVersion {self.version}>'