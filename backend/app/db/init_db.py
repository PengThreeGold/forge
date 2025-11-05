from app.db.database import engine, Base
from app.models import *


def create_tables():
    """
    创建所有数据库表
    """
    Base.metadata.create_all(bind=engine)


def init_permissions():
    """
    初始化权限数据
    """
    from app.db.database import SessionLocal
    from app.models.permission import Permission
    
    db = SessionLocal()
    try:
        # 检查是否已有权限数据
        if db.query(Permission).count() > 0:
            return
        
        # 创建默认权限
        permissions = [
            # 软件管理权限
            {"id": "software:create", "name": "创建软件", "description": "创建和管理软件空间", "category": "软件管理"},
            {"id": "software:read", "name": "查看软件", "description": "查看软件空间信息", "category": "软件管理"},
            {"id": "software:update", "name": "编辑软件", "description": "编辑软件空间信息", "category": "软件管理"},
            {"id": "software:delete", "name": "删除软件", "description": "删除软件空间", "category": "软件管理"},
            
            # 版本管理权限
            {"id": "version:create", "name": "创建版本", "description": "创建和管理软件版本", "category": "版本管理"},
            {"id": "version:read", "name": "查看版本", "description": "查看软件版本信息", "category": "版本管理"},
            {"id": "version:update", "name": "编辑版本", "description": "编辑软件版本信息", "category": "版本管理"},
            {"id": "version:delete", "name": "删除版本", "description": "删除软件版本", "category": "版本管理"},
            {"id": "version:publish", "name": "发布版本", "description": "发布软件版本", "category": "版本管理"},
            
            # 统计分析权限
            {"id": "stats:read", "name": "查看统计", "description": "查看下载统计数据", "category": "统计分析"},
            
            # Webhook权限
            {"id": "webhook:manage", "name": "管理Webhook", "description": "管理Webhook配置", "category": "Webhook"},
            
            # 用户管理权限
            {"id": "user:create", "name": "创建用户", "description": "创建和管理用户账户", "category": "用户管理"},
            {"id": "user:read", "name": "查看用户", "description": "查看用户信息", "category": "用户管理"},
            {"id": "user:update", "name": "编辑用户", "description": "编辑用户信息", "category": "用户管理"},
            {"id": "user:delete", "name": "删除用户", "description": "删除用户账户", "category": "用户管理"},
        ]
        
        for perm_data in permissions:
            permission = Permission(**perm_data)
            db.add(permission)
        
        db.commit()
    finally:
        db.close()


def init_roles():
    """
    初始化角色数据
    """
    from app.db.database import SessionLocal
    from app.models.role import Role
    
    db = SessionLocal()
    try:
        # 检查是否已有角色数据
        if db.query(Role).count() > 0:
            return
        
        # 创建默认角色
        roles = [
            {
                "name": "管理员",
                "description": "系统管理员，拥有所有权限",
                "permissions": '["software:create", "software:read", "software:update", "software:delete", '
                               '"version:create", "version:read", "version:update", "version:delete", "version:publish", '
                               '"stats:read", "webhook:manage", '
                               '"user:create", "user:read", "user:update", "user:delete"]'
            },
            {
                "name": "编辑者",
                "description": "可以编辑和管理软件内容",
                "permissions": '["software:create", "software:read", "software:update", '
                               '"version:create", "version:read", "version:update", "version:delete", "version:publish", '
                               '"stats:read", "webhook:manage"]'
            },
            {
                "name": "查看者",
                "description": "只能查看信息，不能修改",
                "permissions": '["software:read", "version:read", "stats:read"]'
            }
        ]
        
        for role_data in roles:
            role = Role(**role_data)
            db.add(role)
        
        db.commit()
    finally:
        db.close()