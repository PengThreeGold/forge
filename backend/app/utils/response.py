from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import jwt_required, get_jwt_identity


def success_response(data=None, message="操作成功", status_code=200):
    """成功响应"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code


def error_response(message="操作失败", status_code=400, details=None):
    """错误响应"""
    response = {
        "success": False,
        "message": message
    }
    
    if details:
        response["details"] = details
        
    return jsonify(response), status_code


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