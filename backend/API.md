# Forge 软件发布管理平台 - API 文档

本文档提供了 Forge 软件发布管理平台的详细 API 文档，包括认证、软件管理、统计分析等各个模块的接口说明。

## 目录

- [API 概述](#api-概述)
- [认证](#认证)
- [软件管理](#软件管理)
- [软件版本管理](#软件版本管理)
- [文件管理](#文件管理)
- [统计分析](#统计分析)
- [Webhook](#webhook)
- [错误处理](#错误处理)
- [API 示例](#api-示例)

## API 概述

### 基础信息

- **基础URL**: `/api`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 请求格式

所有 API 请求都需要在请求头中包含认证信息（除了登录和注册接口）：

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 响应格式

所有 API 响应都遵循统一的格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

或错误响应：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  },
  "message": "操作失败"
}
```

### HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权，需要登录 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 认证

### 登录

用户登录获取访问令牌。

**请求**

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  },
  "message": "登录成功"
}
```

### 刷新令牌

使用刷新令牌获取新的访问令牌。

**请求**

```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "令牌刷新成功"
}
```

### 获取用户信息

获取当前登录用户的信息。

**请求**

```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "获取用户信息成功"
}
```

### 修改密码

修改当前登录用户的密码。

**请求**

```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "old_password",
  "new_password": "new_password"
}
```

**响应**

```json
{
  "success": true,
  "data": null,
  "message": "密码修改成功"
}
```

### 初始化管理员账户

首次使用时初始化管理员账户（仅当没有管理员时可用）。

**请求**

```http
POST /api/auth/init-admin
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "email": "admin@example.com"
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "管理员创建成功"
}
```

## 软件管理

### 获取软件列表

获取软件空间列表，支持分页、搜索和排序。

**请求**

```http
GET /api/software?page=1&pageSize=20&search=forge&sortBy=name&order=asc
Authorization: Bearer <access_token>
```

**查询参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认为 1 |
| pageSize | integer | 否 | 每页条数，默认为 20 |
| search | string | 否 | 搜索关键词 |
| sortBy | string | 否 | 排序字段，默认为 created_at |
| order | string | 否 | 排序方向，asc 或 desc，默认为 desc |

**响应**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Forge",
        "description": "软件发布管理平台",
        "status": "active",
        "owner_id": 1,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "versions_count": 3
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  },
  "message": "获取软件列表成功"
}
```

### 获取软件详情

获取指定软件空间的详细信息。

**请求**

```http
GET /api/software/1
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Forge",
    "description": "软件发布管理平台",
    "status": "active",
    "owner_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "versions_count": 3,
    "owner": {
      "id": 1,
      "username": "admin"
    }
  },
  "message": "获取软件详情成功"
}
```

### 创建软件空间

创建新的软件空间。

**请求**

```http
POST /api/software
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Forge",
  "description": "软件发布管理平台"
}
```

**请求体参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| name | string | 是 | 软件名称 |
| description | string | 是 | 软件描述 |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Forge",
    "description": "软件发布管理平台",
    "status": "active",
    "owner_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "软件创建成功"
}
```

### 更新软件空间

更新指定软件空间的信息。

**请求**

```http
PUT /api/software/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Forge Updated",
  "description": "软件发布管理平台（更新版）",
  "status": "active"
}
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**请求体参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| name | string | 否 | 软件名称 |
| description | string | 否 | 软件描述 |
| status | string | 否 | 软件状态，active 或 inactive |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Forge Updated",
    "description": "软件发布管理平台（更新版）",
    "status": "active",
    "owner_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "软件更新成功"
}
```

### 删除软件空间

删除指定的软件空间及其所有版本和文件。

**请求**

```http
DELETE /api/software/1
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": null,
  "message": "软件删除成功"
}
```

### 切换软件状态

切换软件空间的上下架状态。

**请求**

```http
PUT /api/software/1/toggle-status
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Forge",
    "description": "软件发布管理平台",
    "status": "inactive",
    "owner_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "软件状态切换成功"
}
```

## 软件版本管理

### 获取软件版本列表

获取指定软件空间的所有版本。

**请求**

```http
GET /api/software/1/versions
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "version_number": "1.0.0",
      "release_notes": "初始版本",
      "file_size": 52428800,
      "file_hash": "a1b2c3d4e5f6...",
      "software_id": 1,
      "uploader_id": 1,
      "status": "active",
      "created_at": "2023-01-01T00:00:00Z",
      "download_count": 10
    },
    {
      "id": 2,
      "version_number": "1.1.0",
      "release_notes": "修复了一些问题",
      "file_size": 53477376,
      "file_hash": "f6e5d4c3b2a1...",
      "software_id": 1,
      "uploader_id": 1,
      "status": "active",
      "created_at": "2023-01-02T00:00:00Z",
      "download_count": 5
    }
  ],
  "message": "获取软件版本列表成功"
}
```

### 获取软件版本详情

获取指定软件版本的详细信息。

**请求**

```http
GET /api/software/1/versions/1
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |
| version_id | integer | 是 | 软件版本 ID |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "version_number": "1.0.0",
    "release_notes": "初始版本",
    "file_size": 52428800,
    "file_hash": "a1b2c3d4e5f6...",
    "software_id": 1,
    "uploader_id": 1,
    "status": "active",
    "created_at": "2023-01-01T00:00:00Z",
    "download_count": 10,
    "software": {
      "id": 1,
      "name": "Forge"
    },
    "uploader": {
      "id": 1,
      "username": "admin"
    }
  },
  "message": "获取软件版本详情成功"
}
```

### 上传软件版本

为指定软件空间上传新版本。

**请求**

```http
POST /api/software/1/versions
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

version_number=1.2.0&release_notes=新版本发布
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**表单参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| file | file | 是 | 软件文件 |
| version_number | string | 是 | 版本号 |
| release_notes | string | 否 | 发布说明 |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 3,
    "version_number": "1.2.0",
    "release_notes": "新版本发布",
    "file_size": 54525952,
    "file_hash": "9f8e7d6c5b4a...",
    "software_id": 1,
    "uploader_id": 1,
    "status": "active",
    "created_at": "2023-01-03T00:00:00Z",
    "download_count": 0
  },
  "message": "版本上传成功"
}
```

### 更新软件版本

更新指定软件版本的信息。

**请求**

```http
PUT /api/software/1/versions/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "version_number": "1.0.1",
  "release_notes": "修复了一些问题",
  "status": "active"
}
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |
| version_id | integer | 是 | 软件版本 ID |

**请求体参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| version_number | string | 否 | 版本号 |
| release_notes | string | 否 | 发布说明 |
| status | string | 否 | 版本状态，active 或 inactive |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "version_number": "1.0.1",
    "release_notes": "修复了一些问题",
    "file_size": 52428800,
    "file_hash": "a1b2c3d4e5f6...",
    "software_id": 1,
    "uploader_id": 1,
    "status": "active",
    "created_at": "2023-01-01T00:00:00Z",
    "download_count": 10
  },
  "message": "版本更新成功"
}
```

### 删除软件版本

删除指定的软件版本及其文件。

**请求**

```http
DELETE /api/software/1/versions/1
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |
| version_id | integer | 是 | 软件版本 ID |

**响应**

```json
{
  "success": true,
  "data": null,
  "message": "版本删除成功"
}
```

## 文件管理

### 下载软件

下载指定版本的软件文件。

**请求**

```http
GET /api/software/1/versions/1/download
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |
| version_id | integer | 是 | 软件版本 ID |

**响应**

响应为文件流，包含以下头信息：

```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="forge-1.0.0.exe"
Content-Length: 52428800
```

### 公开下载软件

无需认证即可下载指定版本的软件文件（如果软件空间是公开的）。

**请求**

```http
GET /api/public/software/1/versions/1/download
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |
| version_id | integer | 是 | 软件版本 ID |

**响应**

响应为文件流，包含以下头信息：

```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="forge-1.0.0.exe"
Content-Length: 52428800
```

## 统计分析

### 获取软件统计信息

获取指定软件空间的统计信息。

**请求**

```http
GET /api/software/1/statistics
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": {
    "software_id": 1,
    "software_name": "Forge",
    "version_count": 3,
    "total_downloads": 15,
    "version_stats": [
      {
        "version_id": 1,
        "version_number": "1.0.0",
        "download_count": 10,
        "created_at": "2023-01-01T00:00:00Z"
      },
      {
        "version_id": 2,
        "version_number": "1.1.0",
        "download_count": 5,
        "created_at": "2023-01-02T00:00:00Z"
      }
    ],
    "daily_stats": [
      {
        "date": "2023-01-01",
        "count": 10
      },
      {
        "date": "2023-01-02",
        "count": 5
      }
    ]
  },
  "message": "获取软件统计信息成功"
}
```

### 获取下载记录

获取指定软件空间的下载记录。

**请求**

```http
GET /api/software/1/downloads?page=1&pageSize=20&startDate=2023-01-01&endDate=2023-01-31
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**查询参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认为 1 |
| pageSize | integer | 否 | 每页条数，默认为 20 |
| startDate | string | 否 | 开始日期，格式 YYYY-MM-DD |
| endDate | string | 否 | 结束日期，格式 YYYY-MM-DD |

**响应**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "downloaded_at": "2023-01-01T10:00:00Z",
        "version": {
          "id": 1,
          "version_number": "1.0.0"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  },
  "message": "获取下载记录成功"
}
```

### 获取系统统计信息

获取系统的整体统计信息（仅管理员可用）。

**请求**

```http
GET /api/statistics/system
Authorization: Bearer <access_token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "total_software": 10,
    "total_versions": 25,
    "total_downloads": 1000,
    "active_software": 8,
    "inactive_software": 2,
    "daily_downloads": [
      {
        "date": "2023-01-01",
        "count": 50
      },
      {
        "date": "2023-01-02",
        "count": 30
      }
    ],
    "top_software": [
      {
        "id": 1,
        "name": "Forge",
        "download_count": 500
      },
      {
        "id": 2,
        "name": "Tool",
        "download_count": 300
      }
    ]
  },
  "message": "获取系统统计信息成功"
}
```

## Webhook

### 配置 Webhook

配置指定软件空间的 Webhook。

**请求**

```http
POST /api/software/1/webhook
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "secret": "webhook_secret",
  "events": ["download", "create", "update"]
}
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**请求体参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| url | string | 是 | Webhook URL |
| secret | string | 否 | Webhook 密钥，用于验证请求 |
| events | array | 否 | 触发事件列表，可选值：download, create, update, delete |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "url": "https://example.com/webhook",
    "secret": "webhook_secret",
    "events": ["download", "create", "update"],
    "software_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "Webhook 配置成功"
}
```

### 获取 Webhook 配置

获取指定软件空间的 Webhook 配置。

**请求**

```http
GET /api/software/1/webhook
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "url": "https://example.com/webhook",
    "secret": "webhook_secret",
    "events": ["download", "create", "update"],
    "software_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "获取 Webhook 配置成功"
}
```

### 更新 Webhook 配置

更新指定软件空间的 Webhook 配置。

**请求**

```http
PUT /api/software/1/webhook
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://example.com/webhook-updated",
  "secret": "new_webhook_secret",
  "events": ["download", "create"]
}
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**请求体参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| url | string | 否 | Webhook URL |
| secret | string | 否 | Webhook 密钥，用于验证请求 |
| events | array | 否 | 触发事件列表，可选值：download, create, update, delete |

**响应**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "url": "https://example.com/webhook-updated",
    "secret": "new_webhook_secret",
    "events": ["download", "create"],
    "software_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "Webhook 更新成功"
}
```

### 删除 Webhook 配置

删除指定软件空间的 Webhook 配置。

**请求**

```http
DELETE /api/software/1/webhook
Authorization: Bearer <access_token>
```

**路径参数**

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 软件空间 ID |

**响应**

```json
{
  "success": true,
  "data": null,
  "message": "Webhook 删除成功"
}
```

### Webhook 事件

以下是可能触发 Webhook 的事件类型及其数据格式：

#### 下载事件

当软件被下载时触发。

```json
{
  "event": "download",
  "timestamp": "2023-01-01T10:00:00Z",
  "software_id": 1,
  "software_name": "Forge",
  "version_id": 1,
  "version_number": "1.0.0",
  "download": {
    "id": 1,
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
}
```

#### 创建事件

当软件空间或版本被创建时触发。

```json
{
  "event": "create",
  "timestamp": "2023-01-01T10:00:00Z",
  "software_id": 1,
  "software_name": "Forge"
}
```

#### 更新事件

当软件空间或版本被更新时触发。

```json
{
  "event": "update",
  "timestamp": "2023-01-01T10:00:00Z",
  "software_id": 1,
  "software_name": "Forge"
}
```

#### 删除事件

当软件空间或版本被删除时触发。

```json
{
  "event": "delete",
  "timestamp": "2023-01-01T10:00:00Z",
  "software_id": 1,
  "software_name": "Forge"
}
```

## 错误处理

### 错误码

| 错误码 | 描述 |
|--------|------|
| INVALID_PARAMETER | 请求参数无效 |
| MISSING_PARAMETER | 缺少必需参数 |
| INVALID_CREDENTIALS | 用户名或密码错误 |
| UNAUTHORIZED | 未授权访问 |
| FORBIDDEN | 权限不足 |
| RESOURCE_NOT_FOUND | 资源不存在 |
| RESOURCE_ALREADY_EXISTS | 资源已存在 |
| FILE_UPLOAD_FAILED | 文件上传失败 |
| INVALID_FILE_TYPE | 无效的文件类型 |
| FILE_TOO_LARGE | 文件过大 |
| WEBHOOK_FAILED | Webhook 调用失败 |
| INTERNAL_ERROR | 服务器内部错误 |

### 错误响应示例

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "请求参数无效"
  },
  "message": "操作失败"
}
```

## API 示例

### 使用 curl

#### 登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### 获取软件列表

```bash
curl -X GET http://localhost:5000/api/software \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### 创建软件

```bash
curl -X POST http://localhost:5000/api/software \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Software", "description": "A test software"}'
```

#### 上传软件版本

```bash
curl -X POST http://localhost:5000/api/software/1/versions \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -F "file=@/path/to/software.exe" \
  -F "version_number=1.0.0" \
  -F "release_notes=Initial release"
```

### 使用 JavaScript (Axios)

#### 登录

```javascript
import axios from 'axios';

async function login(username, password) {
  try {
    const response = await axios.post('/api/auth/login', {
      username,
      password
    });
    
    const { access_token } = response.data.data;
    localStorage.setItem('token', access_token);
    
    return access_token;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}

// 使用示例
login('admin', 'admin123')
  .then(token => {
    console.log('Login successful, token:', token);
  })
  .catch(error => {
    console.error('Login failed:', error);
  });
```

#### 获取软件列表

```javascript
import axios from 'axios';

async function getSoftwareList(page = 1, pageSize = 20, search = '') {
  try {
    const token = localStorage.getItem('token');
    
    const response = await axios.get('/api/software', {
      params: {
        page,
        pageSize,
        search
      },
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Failed to get software list:', error);
    throw error;
  }
}

// 使用示例
getSoftwareList(1, 20, 'forge')
  .then(data => {
    console.log('Software list:', data);
  })
  .catch(error => {
    console.error('Failed to get software list:', error);
  });
```

#### 上传软件版本

```javascript
import axios from 'axios';

async function uploadSoftwareVersion(softwareId, file, versionNumber, releaseNotes) {
  try {
    const token = localStorage.getItem('token');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('version_number', versionNumber);
    formData.append('release_notes', releaseNotes);
    
    const response = await axios.post(`/api/software/${softwareId}/versions`, formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Failed to upload software version:', error);
    throw error;
  }
}

// 使用示例
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

uploadSoftwareVersion(1, file, '1.0.0', 'Initial release')
  .then(data => {
    console.log('Upload successful:', data);
  })
  .catch(error => {
    console.error('Upload failed:', error);
  });
```

### 使用 Python (requests)

#### 登录

```python
import requests

def login(username, password):
    try:
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json={
                'username': username,
                'password': password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['access_token']
        else:
            raise Exception(f'Login failed: {response.status_code}')
    except Exception as e:
        print(f'Error during login: {e}')
        raise

# 使用示例
try:
    token = login('admin', 'admin123')
    print(f'Login successful, token: {token}')
except Exception as e:
    print(f'Login failed: {e}')
```

#### 获取软件列表

```python
import requests

def get_software_list(token, page=1, page_size=20, search=''):
    try:
        response = requests.get(
            'http://localhost:5000/api/software',
            params={
                'page': page,
                'pageSize': page_size,
                'search': search
            },
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']
        else:
            raise Exception(f'Failed to get software list: {response.status_code}')
    except Exception as e:
        print(f'Error getting software list: {e}')
        raise

# 使用示例
try:
    token = 'your-access-token'
    software_list = get_software_list(token, 1, 20, 'forge')
    print(f'Software list: {software_list}')
except Exception as e:
    print(f'Failed to get software list: {e}')
```

#### 上传软件版本

```python
import requests

def upload_software_version(token, software_id, file_path, version_number, release_notes):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'version_number': version_number,
                'release_notes': release_notes
            }
            
            response = requests.post(
                f'http://localhost:5000/api/software/{software_id}/versions',
                files=files,
                data=data,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
        
        if response.status_code == 201:
            data = response.json()
            return data['data']
        else:
            raise Exception(f'Failed to upload software version: {response.status_code}')
    except Exception as e:
        print(f'Error uploading software version: {e}')
        raise

# 使用示例
try:
    token = 'your-access-token'
    upload_software_version(token, 1, '/path/to/software.exe', '1.0.0', 'Initial release')
    print('Upload successful')
except Exception as e:
    print(f'Failed to upload software version: {e}')
```

通过以上 API 文档，您应该能够了解如何使用 Forge 软件发布管理平台的各种接口。如果您有任何问题，请参考开发指南或联系开发团队。