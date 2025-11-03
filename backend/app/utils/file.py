import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions=None):
    """检查文件类型是否允许"""
    if not allowed_extensions:
        allowed_extensions = {'exe', 'msi', 'dmg', 'pkg', 'deb', 'rpm', 'zip', 'tar', 'gz', 'rar', '7z'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(file, upload_folder=None, subfolder=None):
    """保存上传的文件"""
    if not file:
        return None, "没有提供文件"
    
    if not allowed_file(file.filename):
        return None, "不支持的文件类型"
    
    # 确保目录存在
    if not upload_folder:
        upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if subfolder:
        target_folder = os.path.join(upload_folder, subfolder)
    else:
        target_folder = upload_folder
    
    os.makedirs(target_folder, exist_ok=True)
    
    # 安全的文件名
    filename = secure_filename(file.filename)
    
    # 添加随机前缀避免文件名冲突
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # 保存文件
    file_path = os.path.join(target_folder, unique_filename)
    file.save(file_path)
    
    # 计算文件哈希
    file_hash = calculate_file_hash(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    return {
        'filename': unique_filename,
        'original_filename': filename,
        'file_path': file_path,
        'file_hash': file_hash,
        'file_size': file_size
    }, "文件上传成功"


def calculate_file_hash(file_path):
    """计算文件SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def move_file_to_storage(source_path, software_space_id, version):
    """将文件从上传目录移动到软件存储目录"""
    # 确保目标目录存在
    storage_folder = current_app.config['SOFTWARE_STORAGE']
    target_folder = os.path.join(storage_folder, str(software_space_id))
    os.makedirs(target_folder, exist_ok=True)
    
    # 构建目标文件路径
    filename = os.path.basename(source_path)
    target_path = os.path.join(target_folder, f"v{version}_{filename}")
    
    # 移动文件
    try:
        import shutil
        shutil.move(source_path, target_path)
        return target_path, "文件移动成功"
    except Exception as e:
        return None, f"文件移动失败: {str(e)}"


def delete_file(file_path):
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True, "文件删除成功"
        return False, "文件不存在"
    except Exception as e:
        return False, f"文件删除失败: {str(e)}"


def get_file_size_human_readable(size_bytes):
    """将文件大小转换为人类可读格式"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    double_size = size_bytes
    
    while double_size >= 1024 and i < len(size_names)-1:
        double_size /= 1024.0
        i += 1
    
    return f"{double_size:.2f}{size_names[i]}"


def validate_file_integrity(file_path, expected_hash):
    """验证文件完整性"""
    if not os.path.exists(file_path):
        return False, "文件不存在"
    
    actual_hash = calculate_file_hash(file_path)
    
    if actual_hash == expected_hash:
        return True, "文件完整性验证通过"
    else:
        return False, "文件完整性验证失败，哈希值不匹配"