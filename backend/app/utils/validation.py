import os
from typing import List, Optional

from app.core.config import settings


def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
    """
    验证文件大小是否在允许范围内
    
    Args:
        file_size: 文件大小（字节）
        max_size: 最大允许大小（字节），默认使用配置中的最大大小
    
    Returns:
        文件大小是否有效
    """
    if max_size is None:
        max_size = settings.MAX_FILE_SIZE
    
    return file_size <= max_size


def validate_file_type(filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    验证文件类型是否允许
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的文件扩展名列表
    
    Returns:
        文件类型是否有效
    """
    if not allowed_extensions:
        return True
    
    # 获取文件扩展名
    file_ext = os.path.splitext(filename)[1].lower()
    
    # 检查是否在允许列表中
    return file_ext in allowed_extensions


def validate_space_id(space_id: str) -> bool:
    """
    验证软件空间ID格式
    
    Args:
        space_id: 软件空间ID
    
    Returns:
        ID格式是否有效
    """
    import re
    
    # 8位随机字符，只包含数字与小写字母
    pattern = r'^[a-z0-9]{8}$'
    return bool(re.match(pattern, space_id))


def validate_api_key(api_key: str) -> bool:
    """
    验证API密钥格式
    
    Args:
        api_key: API密钥
    
    Returns:
        API密钥格式是否有效
    """
    import re
    
    # 40-60位字符，只包含字母和数字
    pattern = r'^[a-zA-Z0-9]{40,60}$'
    return bool(re.match(pattern, api_key))


def validate_version_format(version: str) -> bool:
    """
    验证版本号格式
    
    Args:
        version: 版本号
    
    Returns:
        版本号格式是否有效
    """
    import re
    
    # 简单的语义版本号验证
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    return bool(re.match(pattern, version))


def validate_webhook_url(url: str) -> bool:
    """
    验证Webhook URL格式
    
    Args:
        url: Webhook URL
    
    Returns:
        URL格式是否有效
    """
    import re
    
    # 简单的URL格式验证
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_username(username: str) -> bool:
    """
    验证用户名格式
    
    Args:
        username: 用户名
    
    Returns:
        用户名格式是否有效
    """
    import re
    
    # 3-50位字符，只允许字母、数字和下划线
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, username))


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        邮箱格式是否有效
    """
    import re
    
    # 简单的邮箱格式验证
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """
    验证密码强度
    
    Args:
        password: 密码
    
    Returns:
        (是否有效, 错误消息列表)
    """
    errors = []
    
    # 检查长度
    if len(password) < 6:
        errors.append("密码长度至少6位")
    
    if len(password) > 100:
        errors.append("密码长度不能超过100位")
    
    # 检查复杂度（可选）
    # if not any(c.isupper() for c in password):
    #     errors.append("密码必须包含至少一个大写字母")
    # 
    # if not any(c.islower() for c in password):
    #     errors.append("密码必须包含至少一个小写字母")
    # 
    # if not any(c.isdigit() for c in password):
    #     errors.append("密码必须包含至少一个数字")
    
    return len(errors) == 0, errors