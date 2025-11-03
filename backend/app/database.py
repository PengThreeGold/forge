from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import db

# 获取当前app的数据库URI
def get_database_uri():
    from flask import current_app
    return current_app.config['SQLALCHEMY_DATABASE_URI']

# 创建引擎
def create_engine_from_app():
    uri = get_database_uri()
    return create_engine(uri)

# 创建会话工厂
def create_session_factory():
    engine = create_engine_from_app()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 初始化数据库
def init_db():
    """初始化数据库，创建所有表"""
    from app.models.user import User
    from app.models.software import SoftwareSpace, SoftwareVersion
    from app.models.statistics import DownloadRecord, WebhookLog
    
    db.create_all()

# 重置数据库
def reset_db():
    """重置数据库，删除所有表并重新创建"""
    from app.models.user import User
    from app.models.software import SoftwareSpace, SoftwareVersion
    from app.models.statistics import DownloadRecord, WebhookLog
    
    db.drop_all()
    db.create_all()