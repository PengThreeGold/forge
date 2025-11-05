from typing import List, Optional
import os
import secrets
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # FastAPI 配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Forge 软件发布管理平台"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Forge 是一个现代化的软件发布管理平台，旨在帮助开发团队更高效地管理和发布软件版本。"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 1110
    DEBUG: bool = True
    
    # 数据库配置
    SQLITE_DB_PATH: str = "forge.db"
    
    # CORS配置
    CORS_ORIGINS: str = "*"
    
    def get_cors_origins(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [i.strip() for i in self.CORS_ORIGINS.split(",")]
    
    # JWT配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # HTTPS配置
    HTTPS_ENABLED: bool = False
    SSL_CERT_PATH: str = "certs/localhost.crt"
    SSL_KEY_PATH: str = "certs/localhost.key"
    
    # 文件存储配置
    UPLOAD_DIR: str = "storage/uploads"
    MAX_FILE_SIZE: int = 1024 * 1024 * 1024  # 1GB
    
    # Webhook配置
    WEBHOOK_TIMEOUT: int = 10  # 10秒
    WEBHOOK_MAX_RETRIES: int = 3
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()