from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import mimetypes
from contextlib import asynccontextmanager

# 修复 Windows 下 MIME 类型问题
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

from app.core.config import settings
from app.db.database import engine
from app.db.init_db import create_tables, init_permissions, init_roles
from app.api import auth_router, users_router, spaces_router, versions_router, public_router, stats_router, webhooks_router, permissions_router
from app.schemas.common import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    # 创建数据库表
    create_tables()

    # 初始化权限和角色数据
    init_permissions()
    init_roles()

    # 确保上传目录存在
    upload_dir = settings.UPLOAD_DIR
    if upload_dir and not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    yield

    # 关闭时执行
    pass


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
    ],
    expose_headers=["Content-Range", "X-Content-Range"],
    max_age=86400,
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="服务器内部错误",
            error={
                "code": "INTERNAL_ERROR",
                "message": str(exc)
            }
        ).dict()
    )


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """404异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            success=False,
            message="资源不存在",
            error={
                "code": "RESOURCE_NOT_FOUND",
                "message": "请求的资源不存在"
            }
        ).dict()
    )


@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc):
    """401异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            success=False,
            message="未授权，请登录",
            error={
                "code": "UNAUTHORIZED",
                "message": "未授权访问"
            }
        ).dict()
    )


@app.exception_handler(403)
async def forbidden_exception_handler(request: Request, exc):
    """403异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ErrorResponse(
            success=False,
            message="禁止访问",
            error={
                "code": "FORBIDDEN",
                "message": "权限不足"
            }
        ).dict()
    )


@app.exception_handler(400)
async def bad_request_exception_handler(request: Request, exc):
    """400异常处理器"""
    detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            success=False,
            message="请求参数错误",
            error={
                "code": "BAD_REQUEST",
                "message": detail
            }
        ).dict()
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }


# 注册API路由
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["认证"]
)

app.include_router(
    users_router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["用户管理"]
)

app.include_router(
    spaces_router,
    prefix=f"{settings.API_V1_STR}/spaces",
    tags=["软件管理"]
)

app.include_router(
    versions_router,
    prefix=f"{settings.API_V1_STR}/spaces",
    tags=["版本管理"]
)

app.include_router(
    public_router,
    prefix=f"{settings.API_V1_STR}/public",
    tags=["公共API"]
)

app.include_router(
    stats_router,
    prefix=f"{settings.API_V1_STR}/stats",
    tags=["统计分析"]
)

app.include_router(
    webhooks_router,
    prefix=f"{settings.API_V1_STR}/spaces",
    tags=["Webhook"]
)

app.include_router(
    permissions_router,
    prefix=f"{settings.API_V1_STR}/permissions",
    tags=["权限管理"]
)


# 挂载静态文件（前端构建产物）
# 注意：app.mount() 必须在所有路由之前注册，但 catch-all 路由除外
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    # 挂载 assets 目录 - 这会优先匹配 /assets/* 路径
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# 前端 SPA 路由处理（必须放在所有其他路由之后）
@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request):
    """
    Catch-all 路由：处理前端 SPA 路由
    必须放在所有 API 路由之后，这样 API 路由才能优先匹配
    """
    # API 路径已经被路由处理，如果到这里说明是无效的 API
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # assets 路径已被 app.mount 处理，不应该到这里
    if full_path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Static asset not found")
    
    # 检查是否存在静态文件目录
    if not os.path.exists(static_dir):
        return {
            "message": f"欢迎使用 {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
            "api": f"{settings.API_V1_STR}",
            "note": "前端未构建，请运行 start.sh 或 start.bat"
        }
    
    # 尝试作为静态文件提供（处理根目录的文件，如 favicon.ico）
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # 所有其他路径返回 index.html（Vue Router 的 HTML5 History 模式）
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # 如果 index.html 不存在
    return {
        "message": f"欢迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "api": f"{settings.API_V1_STR}",
        "note": "前端未构建，请运行 start.sh 或 start.bat"
    }


if __name__ == "__main__":
    # 开发环境运行
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        timeout_keep_alive=settings.TIMEOUT_KEEP_ALIVE,
        timeout_graceful_shutdown=settings.TIMEOUT_GRACEFUL_SHUTDOWN
    )
