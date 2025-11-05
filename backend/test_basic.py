#!/usr/bin/env python3
"""
基本功能测试脚本
"""

import sys
import os
import asyncio
import httpx
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.database import engine, Base
from app.db.init_db import create_tables, init_permissions, init_roles


def test_database():
    """测试数据库连接和表创建"""
    print("测试数据库连接...")
    
    try:
        # 创建所有表
        create_tables()
        print("✓ 数据库表创建成功")
        
        # 初始化基础数据
        init_permissions()
        init_roles()
        print("✓ 基础数据初始化成功")
        
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False


def test_imports():
    """测试关键模块导入"""
    print("测试模块导入...")
    
    modules_to_test = [
        "app.core.security",
        "app.core.deps", 
        "app.crud.user",
        "app.crud.software_space",
        "app.crud.software_version",
        "app.utils.file",
        "app.utils.webhook",
        "app.utils.validation"
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} 导入成功")
            success_count += 1
        except Exception as e:
            print(f"✗ {module_name} 导入失败: {e}")
    
    print(f"模块导入测试结果: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)


async def test_api_startup():
    """测试API启动"""
    print("测试API启动...")
    
    try:
        # 导入主应用
        from app.main import app
        
        # 创建测试客户端
        async with httpx.AsyncClient(app=app, base_url=f"http://{settings.HOST}:{settings.PORT}") as client:
            # 测试根路径
            response = await client.get("/")
            if response.status_code == 200:
                print("✓ 根路径响应正常")
            else:
                print(f"✗ 根路径响应异常: {response.status_code}")
                return False
            
            # 测试健康检查
            response = await client.get("/health")
            if response.status_code == 200:
                print("✓ 健康检查通过")
            else:
                print(f"✗ 健康检查失败: {response.status_code}")
                return False
            
            # 测试API文档
            response = await client.get(f"{settings.API_V1_STR}/docs")
            if response.status_code == 200:
                print("✓ API文档可访问")
            else:
                print(f"✗ API文档访问失败: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ API启动测试失败: {e}")
        return False


def test_directories():
    """测试目录结构"""
    print("测试目录结构...")
    
    required_dirs = [
        "app",
        "app/api",
        "app/core",
        "app/crud",
        "app/db",
        "app/models",
        "app/schemas",
        "app/utils"
    ]
    
    success_count = 0
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path} 目录存在")
            success_count += 1
        else:
            print(f"✗ {dir_path} 目录不存在")
    
    print(f"目录结构测试结果: {success_count}/{len(required_dirs)} 成功")
    return success_count == len(required_dirs)


def test_config():
    """测试配置加载"""
    print("测试配置加载...")
    
    try:
        # 检查关键配置项
        required_configs = [
            "PROJECT_NAME",
            "VERSION",
            "API_V1_STR",
            "HOST",
            "PORT",
            "SQLITE_DB_PATH",
            "SECRET_KEY",
            "UPLOAD_DIR"
        ]
        
        success_count = 0
        for config_name in required_configs:
            if hasattr(settings, config_name):
                print(f"✓ {config_name} 配置加载成功")
                success_count += 1
            else:
                print(f"✗ {config_name} 配置缺失")
        
        print(f"配置加载测试结果: {success_count}/{len(required_configs)} 成功")
        return success_count == len(required_configs)
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("开始 Forge 软件发布管理平台 基本功能测试\n")
    
    # 运行各项测试
    test_results = []
    
    # 目录结构测试
    test_results.append(("目录结构", test_directories()))
    
    # 配置加载测试
    test_results.append(("配置加载", test_config()))
    
    # 模块导入测试
    test_results.append(("模块导入", test_imports()))
    
    # 数据库测试
    test_results.append(("数据库", test_database()))
    
    # API启动测试
    test_results.append(("API启动", await test_api_startup()))
    
    # 输出测试结果
    print("\n测试结果汇总:")
    passed_tests = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n总体结果: {passed_tests}/{len(test_results)} 测试通过")
    
    if passed_tests == len(test_results):
        print("\n🎉 所有基本功能测试通过！后端服务器基本功能正常。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查相关功能实现。")
        return False


if __name__ == "__main__":
    asyncio.run(main())