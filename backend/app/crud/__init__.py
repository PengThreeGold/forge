from .base import CRUDBase
from .user import CRUDUser, crud_user
from .software_space import CRUDSoftwareSpace, crud_software_space
from .software_version import CRUDSoftwareVersion, crud_software_version
from .download_record import CRUDDownloadRecord, crud_download_record
from .webhook_log import CRUDWebhookLog, crud_webhook_log

# 创建一个简单的命名空间
class CRUD:
    user = crud_user
    software_space = crud_software_space
    software_version = crud_software_version
    download_record = crud_download_record
    webhook_log = crud_webhook_log

# 导出CRUD实例
crud = CRUD()

__all__ = [
    "CRUDBase",
    "CRUDUser",
    "CRUDSoftwareSpace", 
    "CRUDSoftwareVersion",
    "CRUDDownloadRecord",
    "CRUDWebhookLog",
    "crud_user",
    "crud_software_space",
    "crud_software_version", 
    "crud_download_record",
    "crud_webhook_log",
    "crud"
]