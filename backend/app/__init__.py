import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config=None):
    app = Flask(__name__)
    
    # 加载配置
    if config == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # 配置CORS以允许前端访问
    # 支持从配置中获取允许的源，如果未配置则允许所有源
    allowed_origins = app.config.get('CORS_ORIGINS', ["*"])
    
    # 如果允许所有源，则设置为 "*" 以简化配置
    if "*" in allowed_origins:
        cors.init_app(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-CSRF-Token",
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection"
                ],
                "supports_credentials": False,  # 当 origins 为 "*" 时，必须为 False
                "expose_headers": ["Content-Range", "X-Content-Range"]
            }
        })
    else:
        cors.init_app(app, resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-CSRF-Token",
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection"
                ],
                "supports_credentials": True,
                "expose_headers": ["Content-Range", "X-Content-Range"]
            }
        })
    limiter.init_app(app)
    
    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.software import software_bp
    from app.api.statistics import statistics_bp
    from app.api.webhook import webhook_bp
    from app.api.user_management import user_management_bp
    from app.api.permission import permission_bp
    from app.api.system import system_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(software_bp, url_prefix='/api')
    app.register_blueprint(statistics_bp, url_prefix='/api')
    app.register_blueprint(webhook_bp, url_prefix='/api')
    app.register_blueprint(user_management_bp, url_prefix='/api')
    app.register_blueprint(permission_bp, url_prefix='/api')
    app.register_blueprint(system_bp, url_prefix='/api')
    
    # 注册错误处理
    from app.utils.response import register_error_handlers
    register_error_handlers(app)
    
    # 确保所有响应都包含CORS头（防止某些扩展或错误处理绕过CORS添加）
    from app.utils.response import add_cors_headers

    @app.after_request
    def apply_cors(response):
        try:
            add_cors_headers(response)
        except Exception:
            # 不应阻塞正常响应流程，如果添加CORS失败，还是返回原始响应
            app.logger.exception('添加CORS头时发生异常')
        return response
    # 创建存储目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SOFTWARE_STORAGE'], exist_ok=True)
    
    return app