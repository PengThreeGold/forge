from app.utils.auth import authenticate_user, verify_token
from app.models.user import User
from app import db


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def login(username, password):
        """用户登录"""
        user = authenticate_user(username, password)
        
        if not user:
            return None, "用户名或密码错误"
        
        if user.role != 'admin':
            return None, "权限不足"
        
        # 生成令牌
        from flask_jwt_extended import create_access_token, create_refresh_token
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }, "登录成功"
    
    @staticmethod
    def verify_token(token):
        """验证令牌"""
        user_id = verify_token(token)
        
        if not user_id:
            return None, "令牌无效或已过期"
        
        user = User.query.get(user_id)
        
        if not user:
            return None, "用户不存在"
        
        return user, "令牌有效"
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        return User.query.get(user_id)
    
    @staticmethod
    def create_admin_user(username, password, email=None):
        """创建管理员用户"""
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return None, "用户名已存在"
        
        # 创建新用户
        user = User(
            username=username,
            password=password,
            email=email,
            role='admin'
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, "管理员用户创建成功"
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        user = User.query.get(user_id)
        
        if not user:
            return False, "用户不存在"
        
        if not user.check_password(old_password):
            return False, "原密码错误"
        
        user.set_password(new_password)
        db.session.commit()
        
        return True, "密码修改成功"
    
    @staticmethod
    def is_admin(user):
        """检查用户是否为管理员"""
        return user and user.role == 'admin'