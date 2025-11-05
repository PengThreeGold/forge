#!/usr/bin/env python3
"""
测试API接口修改后的功能
测试版本号(string)参数和合并的下载接口
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:1110/api"

# 测试用的API密钥
TEST_API_KEY = "test_api_key_123"

def test_version_operations():
    """测试版本管理接口"""
    print("=== 测试版本管理接口 ===")
    
    # 测试空间ID
    space_id = "test_space"
    
    # 测试版本号
    test_version = "1.0.0"
    
    print(f"1. 测试获取版本列表...")
    try:
        response = requests.get(f"{BASE_URL}/spaces/{space_id}/versions", 
                              headers={"X-API-Key": TEST_API_KEY})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   找到 {data.get('total', 0)} 个版本")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print(f"\n2. 测试使用版本号更新版本信息...")
    try:
        update_data = {
            "release_note": "测试更新版本说明",
            "documentation_url": "https://example.com/docs"
        }
        response = requests.put(f"{BASE_URL}/spaces/{space_id}/versions/{test_version}",
                              json=update_data,
                              headers={"X-API-Key": TEST_API_KEY})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   版本更新成功")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print(f"\n3. 测试使用版本号发布版本...")
    try:
        response = requests.post(f"{BASE_URL}/spaces/{space_id}/versions/{test_version}/publish",
                               headers={"X-API-Key": TEST_API_KEY})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   版本发布成功")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")

def test_download_interfaces():
    """测试合并后的下载接口"""
    print("\n=== 测试下载接口 ===")
    
    # 测试空间ID
    space_id = "test_space"
    
    print("1. 测试下载指定版本...")
    try:
        test_version = "1.0.0"
        response = requests.get(f"{BASE_URL}/public/download/{space_id}/{test_version}",
                              params={"api_key": TEST_API_KEY},
                              allow_redirects=False)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   文件下载成功，大小: {len(response.content)} 字节")
        elif response.status_code == 404:
            print("   版本不存在或未发布")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print("\n2. 测试下载最新版本...")
    try:
        response = requests.get(f"{BASE_URL}/public/download/{space_id}/latest",
                              params={"api_key": TEST_API_KEY},
                              allow_redirects=False)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   最新版本下载成功，大小: {len(response.content)} 字节")
        elif response.status_code == 404:
            print("   没有可用的最新版本")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print("\n3. 测试指定架构下载...")
    try:
        test_version = "1.0.0"
        response = requests.get(f"{BASE_URL}/public/download/{space_id}/{test_version}",
                              params={"api_key": TEST_API_KEY, "architecture": "x64"},
                              allow_redirects=False)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   x64架构文件下载成功，大小: {len(response.content)} 字节")
        elif response.status_code == 404:
            print("   指定架构的文件不存在")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")

def test_error_cases():
    """测试错误情况"""
    print("\n=== 测试错误情况 ===")
    
    space_id = "test_space"
    
    print("1. 测试不存在的版本号...")
    try:
        response = requests.get(f"{BASE_URL}/public/download/{space_id}/99.99.99",
                              params={"api_key": TEST_API_KEY})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            print("   正确返回404错误")
        else:
            print(f"   意外结果: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print("\n2. 测试无效的API密钥...")
    try:
        response = requests.get(f"{BASE_URL}/public/download/{space_id}/latest",
                              params={"api_key": "invalid_key"})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 401:
            print("   正确返回401未授权错误")
        else:
            print(f"   意外结果: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")

def main():
    """主测试函数"""
    print("开始测试API接口修改...")
    print(f"API基础URL: {BASE_URL}")
    print("=" * 50)
    
    try:
        # 测试版本管理接口
        test_version_operations()
        
        # 测试下载接口
        test_download_interfaces()
        
        # 测试错误情况
        test_error_cases()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()