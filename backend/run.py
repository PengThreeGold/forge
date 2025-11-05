#!/usr/bin/env python3
"""
Forge 软件发布管理平台 - 运行脚本

使用方法:
    python run.py init-admin  # 初始化管理员账户
    python run.py run          # 启动服务器
    python run.py create-tables # 创建数据库表
    python run.py init-data    # 初始化基础数据
"""

from app.crud.user import crud_user
from app.db.init_db import create_tables, init_permissions, init_roles
from app.db.database import SessionLocal
from app.db.init_db import create_tables as init_create_tables
from app.core.config import settings
import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_tables():
    """创建数据库表"""
    print("正在创建数据库表...")
    init_create_tables()
    print("数据库表创建完成")


def init_data():
    """初始化基础数据"""
    print("正在初始化权限和角色数据...")
    init_permissions()
    init_roles()
    print("基础数据初始化完成")


def init_admin():
    """初始化管理员账户"""
    db = SessionLocal()

    # 检查是否已有管理员
    from app.models.user import User
    admin_user = db.query(User).filter(User.role == "admin").first()
    if admin_user:
        print("系统已存在管理员账户")
        return

    # 获取管理员信息
    print("请输入管理员账户信息:")
    username = input("用户名: ").strip()
    if not username:
        print("用户名不能为空")
        return

    # 检查用户名是否已存在
    if crud_user.get_by_username(db, username=username):
        print("用户名已存在")
        return

    email = input("邮箱 (可选): ").strip() or None
    password = input("密码: ").strip()
    if not password:
        print("密码不能为空")
        return

    confirm_password = input("确认密码: ").strip()
    if password != confirm_password:
        print("两次输入的密码不一致")
        return

    # 创建管理员
    from app.schemas.user import UserCreate
    admin_in = UserCreate(
        username=username,
        email=email,
        password=password,
        role="admin"
    )

    admin_user = crud_user.create(db, obj_in=admin_in)
    print(f"管理员账户创建成功: {admin_user.username}")


def run_server():
    """启动服务器"""
    import uvicorn

    print(f"正在启动 {settings.PROJECT_NAME} 服务器...")
    print(f"服务器地址: http://{settings.HOST}:{settings.PORT}")
    print(f"API文档: http://{settings.HOST}:{settings.PORT}{settings.API_V1_STR}/docs")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Forge 软件发布管理平台运行脚本")
    parser.add_argument(
        "command",
        choices=["init-admin", "run", "create-tables", "init-data"],
        help="要执行的命令"
    )

    args = parser.parse_args()

    if args.command == "init-admin":
        init_admin()
    elif args.command == "run":
        run_server()
    elif args.command == "create-tables":
        create_tables()
    elif args.command == "init-data":
        init_data()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
