from flask import jsonify, request, make_response
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import jwt_required, get_jwt_identity


def success_response(data=None, message="操作成功", status_code=200):
    """成功响应"""
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    response = make_response(jsonify(response_data), status_code)
    
    # 添加CORS头
    add_cors_headers(response)
    
    return response


def error_response(message="操作失败", status_code=400, details=None):
    """错误响应"""
    response_data = {
        "success": False,
        "message": message
    }
    
    if details:
        response_data["details"] = details
        
    response = make_response(jsonify(response_data), status_code)
    
    # 添加CORS头
    add_cors_headers(response)
    
    return response


def add_cors_headers(response):
    """添加CORS头到响应"""
    # 获取允许的源
    from flask import current_app
    allowed_origins = current_app.config.get('CORS_ORIGINS', ["*"])
    
    # 处理请求源
    origin = request.headers.get('Origin', '')
    
    # 如果允许所有源，则使用通配符并且不要设置 Allow-Credentials（浏览器不允许同时为 '*' 和 credentials=true）
    if "*" in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = '*'
        # 不设置 Access-Control-Allow-Credentials，这样浏览器不会因为 '*' 与 credentials 冲突而拒绝
    elif origin and origin in allowed_origins:
        # 如果请求的源在允许列表中，则按请求源返回，并允许携带凭证
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'

    # 添加其他CORS头（统一添加可接受的方法和头列表）
    # 如果这是预检请求，优先使用请求中声明的 Access-Control-Request-* 回显到响应中
    acr_method = request.headers.get('Access-Control-Request-Method')
    acr_headers = request.headers.get('Access-Control-Request-Headers')

    if acr_method:
        response.headers['Access-Control-Allow-Methods'] = acr_method
    else:
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

    if acr_headers:
        # 直接回显请求中声明的头，确保预检验证通过
        response.headers['Access-Control-Allow-Headers'] = acr_headers
    else:
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24小时
    # 如果返回的 Access-Control-Allow-Origin 依赖于请求 Origin，则告诉缓存层该响应依据 Origin 变化
    response.headers['Vary'] = 'Origin'


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response("请求参数错误", 400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        return error_response("未授权，请登录", 401)
    
    @app.errorhandler(403)
    def forbidden(error):
        return error_response("禁止访问", 403)
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response("资源不存在", 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response("方法不允许", 405)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return error_response("服务器内部错误", 500)
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """处理HTTP异常"""
        return error_response(e.description, e.code)
    
    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        """处理未预期的异常"""
        app.logger.error(f"未预期的异常: {str(e)}")
        return error_response("服务器内部错误", 500)
    
    # 添加预检请求处理
    @app.before_request
    def before_request():
        """处理预检请求"""
        if request.method == 'OPTIONS':
            # 返回一个空的 204 响应，并添加 CORS 头以响应预检请求
            response = make_response('', 204)
            add_cors_headers(response)
            return response

        # 对于普通请求，不在此处返回响应；CORS 头会在具体的响应构造时由 flask-cors 或 add_cors_headers 添加
        return None


def admin_required(f):
    """管理员权限装饰器"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from app.models.user import User
        from app import db
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return error_response("需要管理员权限", 403)
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function