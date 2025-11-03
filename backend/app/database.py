# 数据库工具函数和配置
from app import db

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