#!/usr/bin/env python3
"""
Forge API测试脚本
用于测试新增和更新的API接口
"""

import os
import sys
import json
import requests
from datetime import datetime

# 配置
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000/api')
USERNAME = os.environ.get('API_USERNAME', 'admin')
PASSWORD = os.environ.get('API_PASSWORD', 'admin123')

def login():
    """登录获取令牌"""
    url = f"{BASE_URL}/auth/login"
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('access_token')
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {str(e)}")
        return None

def test_api(method, endpoint, data=None, params=None, token=None, expected_status=200):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"\n{'='*50}")
        print(f"测试: {method} {endpoint}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✓ 测试通过")
            if response.content:
                try:
                    result = response.json()
                    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应: {response.text}")
        else:
            print("✗ 测试失败")
            print(f"响应: {response.text}")
        
        return response.status_code == expected_status
    
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("Forge API测试脚本")
    print(f"测试URL: {BASE_URL}")
    print(f"测试用户: {USERNAME}")
    
    # 登录获取令牌
    print("\n正在登录...")
    token = login()
    if not token:
        print("登录失败，无法继续测试")
        sys.exit(1)
    
    print("登录成功，令牌已获取")
    
    # 测试用户管理API
    print("\n\n===== 测试用户管理API =====")
    
    # 获取用户列表
    test_api('GET', '/users', token=token)
    
    # 创建用户
    test_api('POST', '/users', 
             data={'username': 'testuser', 'password': 'testpass', 'email': 'test@example.com', 'role': 'user'}, 
             token=token)
    
    # 测试权限管理API
    print("\n\n===== 测试权限管理API =====")
    
    # 获取权限列表
    test_api('GET', '/permissions', token=token)
    
    # 获取角色列表
    test_api('GET', '/roles', token=token)
    
    # 测试软件空间状态管理API
    print("\n\n===== 测试软件空间状态管理API =====")
    
    # 先创建一个软件空间（假设已有ID为1的空间）
    test_api('PUT', '/software/1/status', 
             data={'active': False}, 
             token=token)
    
    test_api('PUT', '/software/1/status', 
             data={'active': True}, 
             token=token)
    
    # 测试Webhook配置管理API
    print("\n\n===== 测试Webhook配置管理API =====")
    
    # 获取Webhook配置
    test_api('GET', '/software/1/webhook/config', token=token)
    
    # 更新Webhook配置
    test_api('PUT', '/software/1/webhook/config', 
             data={'webhook_url': 'https://example.com/webhook', 
                   'webhook_events': ['download', 'version_publish']}, 
             token=token)
    
    # 重新生成Webhook密钥
    test_api('POST', '/software/1/webhook/regenerate-secret', token=token)
    
    # 测试公开API优化
    print("\n\n===== 测试公开API优化 =====")
    
    # 搜索软件空间
    test_api('GET', '/public/spaces/search', 
             params={'q': 'test'}, 
             token=None)
    
    # 获取最新版本
    test_api('GET', '/public/space/1/versions/latest', token=None)
    
    # 获取版本信息
    test_api('GET', '/public/version/1/info', token=None)
    
    # 测试系统管理API
    print("\n\n===== 测试系统管理API =====")
    
    # 获取系统信息
    test_api('GET', '/system/info', token=token)
    
    # 创建系统备份
    test_api('POST', '/system/backup', token=token)
    
    print("\n\n测试完成！")

if __name__ == '__main__':
    main()