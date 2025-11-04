#!/bin/bash

# CORS 测试脚本
# 用于验证前后端 CORS 配置是否正确

echo "=========================================="
echo "CORS 配置测试脚本"
echo "=========================================="

# 检查后端服务是否运行
echo "1. 检查后端服务状态..."
BACKEND_URL="http://localhost:5000"
if curl -s --output /dev/null --connect-timeout 5 "$BACKEND_URL/api/auth/login"; then
    echo "✓ 后端服务正在运行"
else
    echo "✗ 后端服务未运行或无法访问"
    echo "请先启动后端服务: cd backend && python run.py"
    exit 1
fi

# 检查前端服务是否运行
echo "2. 检查前端服务状态..."
FRONTEND_URL="http://localhost:8080"
if curl -s --output /dev/null --connect-timeout 5 "$FRONTEND_URL"; then
    echo "✓ 前端服务正在运行"
else
    echo "✗ 前端服务未运行或无法访问"
    echo "请先启动前端服务: cd frontend && npm run serve"
    exit 1
fi

# 测试 CORS 预检请求
echo "3. 测试 CORS 预检请求 (OPTIONS)..."
ORIGIN="http://localhost:8080"
METHOD="POST"
HEADERS="Content-Type, Authorization"

response=$(curl -s -i -X OPTIONS \
    -H "Origin: $ORIGIN" \
    -H "Access-Control-Request-Method: $METHOD" \
    -H "Access-Control-Request-Headers: $HEADERS" \
    "$BACKEND_URL/api/auth/login")

if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo "✓ CORS 预检请求成功，服务器返回了必要的头部"
else
    echo "✗ CORS 预检请求失败，服务器未返回必要的头部"
    echo "响应内容:"
    echo "$response"
fi

# 测试简单的跨域 GET 请求
echo "4. 测试跨域 GET 请求..."
response=$(curl -s -i -X GET \
    -H "Origin: $ORIGIN" \
    -H "Accept: application/json" \
    "$BACKEND_URL/api/auth/init-admin")

if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo "✓ 跨域 GET 请求成功，服务器返回了必要的头部"
else
    echo "✗ 跨域 GET 请求失败，服务器未返回必要的头部"
    echo "响应内容:"
    echo "$response"
fi

# 测试带有凭证的跨域请求
echo "5. 测试带有凭证的跨域请求..."
# 首先进行登录以获取 token
login_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Origin: $ORIGIN" \
    -d '{"username":"admin","password":"admin"}' \
    "$BACKEND_URL/api/auth/login")

# 检查登录是否成功
if echo "$login_response" | grep -q "access_token"; then
    echo "✓ 登录成功"
    
    # 提取 token
    token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d '"' -f 4)
    
    # 使用 token 进行需要认证的请求
    auth_response=$(curl -s -i -X GET \
        -H "Authorization: Bearer $token" \
        -H "Origin: $ORIGIN" \
        "$BACKEND_URL/api/auth/profile")
    
    if echo "$auth_response" | grep -q "Access-Control-Allow-Origin"; then
        echo "✓ 带有凭证的跨域请求成功"
    else
        echo "✗ 带有凭证的跨域请求失败"
        echo "响应内容:"
        echo "$auth_response"
    fi
else
    echo "✗ 登录失败，请检查管理员账户是否存在"
    echo "响应内容:"
    echo "$login_response"
fi

echo "=========================================="
echo "测试完成"
echo "=========================================="

# 检查浏览器中的实际跨域情况
echo "6. 浏览器端跨域测试建议:"
echo "- 打开浏览器访问 $FRONTEND_URL"
echo "- 打开浏览器开发者工具 (F12)"
echo "- 尝试登录或其他需要API交互的操作"
echo "- 检查 Network 标签中是否有 CORS 错误"
echo "- 检查 Console 标签中是否有跨域相关错误"
echo ""
echo "如果仍有问题，请检查:"
echo "- 前端环境变量配置 (.env.development)"
echo "- 后端环境变量配置 (.env)"
echo "- 浏览器缓存和扩展程序"
echo "=========================================="