import os
from datetime import timedelta

class BaseConfig:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # HTTPS配置
    HTTPS_ENABLED = os.environ.get('HTTPS_ENABLED', 'False').lower() == 'true'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', 'certs/localhost.crt')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', 'certs/localhost.key')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'storage', 'uploads')
    SOFTWARE_STORAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'storage', 'software')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'forge.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    # 生产环境中应该从环境变量获取真实的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # 生产环境HTTPS配置
    HTTPS_ENABLED = os.environ.get('HTTPS_ENABLED', 'True').lower() == 'true'
    
    # 生产环境数据库路径
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/forge.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'


class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING = True
    # 使用内存数据库进行测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境下的存储目录
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_storage', 'uploads')
    SOFTWARE_STORAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_storage', 'software')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}