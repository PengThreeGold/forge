#!/usr/bin/env python3
"""
数据库初始化脚本
创建新的数据库和表结构
"""

import os
import sys
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord, WebhookLog

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 删除所有表（如果存在）
        print("删除现有表...")
        db.drop_all()
        
        # 创建所有表
        print("创建新表...")
        db.create_all()
        
        # 创建默认管理员用户
        print("创建默认管理员用户...")
        admin = User('admin', 'admin123', 'admin@example.com', 'admin')
        db.session.add(admin)
        
        # 提交更改
        db.session.commit()
        
        print("数据库初始化完成！")
        print("默认管理员账户:")
        print("用户名: admin")
        print("密码: admin123")

def main():
    """主函数"""
    print("Forge数据库初始化工具")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 根据环境变量确定数据库路径
    use_postgres = os.environ.get('USE_POSTGRES', 'false').lower() == 'true'
    
    if use_postgres:
        # PostgreSQL数据库
        postgres_user = os.environ.get('POSTGRES_USER', 'postgres')
        postgres_password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
        postgres_db = os.environ.get('POSTGRES_DB', 'forge')
        postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
        postgres_port = os.environ.get('POSTGRES_PORT', '5432')
        
        db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        print(f"使用PostgreSQL数据库: {postgres_host}:{postgres_port}/{postgres_db}")
    else:
        # SQLite数据库（默认）
        db_path = 'forge.db'  # 使用固定的数据库文件名
        db_uri = f'sqlite:///{db_path}'
        print(f"使用SQLite数据库: {db_path}")
    
    # 如果数据库文件存在，询问是否删除
    if os.path.exists(db_path):
        response = input(f"数据库文件 {db_path} 已存在，是否删除并重新创建？(y/n): ")
        if response.lower() != 'y':
            print("取消初始化")
            sys.exit(0)
        
        try:
            os.remove(db_path)
            print(f"已删除现有数据库文件: {db_path}")
        except Exception as e:
            print(f"删除数据库文件失败: {str(e)}")
            sys.exit(1)
    
    # 设置环境变量，让应用使用指定的数据库
    os.environ['SQLALCHEMY_DATABASE_URI'] = db_uri
    
    # 初始化数据库
    init_database()

if __name__ == '__main__':
    main()