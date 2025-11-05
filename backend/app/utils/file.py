import os
import hashlib
from typing import List


def format_file_size(size_bytes: int) -> str:
    """
    将文件大小（字节）转换为人类可读的格式
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"


def calculate_file_hash(file_path: str) -> str:
    """
    计算文件的SHA-256哈希值
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def ensure_directory_exists(file_path: str) -> None:
    """
    确保文件目录存在
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    """
    return os.path.splitext(filename)[1].lower()


def is_safe_filename(filename: str) -> bool:
    """
    检查文件名是否安全
    """
    # 检查是否包含危险字符
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            return False
    
    # 检查文件名长度
    if len(filename) > 255:
        return False
    
    # 检查是否为空或仅包含空格
    if not filename.strip():
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符
    """
    # 替换危险字符
    replacements = {
        '..': '',
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '',
        '<': '_',
        '>': '_',
        '|': '_'
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename.strip()


def allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    检查文件类型是否允许
    """
    if not allowed_extensions:
        return True
    
    file_ext = get_file_extension(filename)
    return file_ext in allowed_extensions