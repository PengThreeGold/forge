import json
import hashlib
import hmac
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings


async def send_webhook(
    webhook_url: str,
    event_type: str,
    data: Dict[str, Any],
    secret: Optional[str] = None
) -> tuple[bool, Optional[int], Optional[str]]:
    """
    发送Webhook请求
    
    Args:
        webhook_url: Webhook URL
        event_type: 事件类型
        data: 事件数据
        secret: Webhook密钥（可选）
    
    Returns:
        (成功状态, 响应状态码, 响应内容)
    """
    try:
        # 构建请求数据
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # 如果提供了密钥，生成签名
        headers = {"Content-Type": "application/json"}
        if secret:
            signature = generate_webhook_signature(payload, secret)
            headers["X-Webhook-Signature"] = signature
        
        # 发送请求
        async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers=headers
            )
            
            return (
                response.status_code < 400,
                response.status_code,
                response.text
            )
    except Exception as e:
        return False, None, str(e)


def generate_webhook_signature(payload: Dict[str, Any], secret: str) -> str:
    """
    生成Webhook签名
    
    Args:
        payload: 请求数据
        secret: 密钥
    
    Returns:
        HMAC-SHA256 签名
    """
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def verify_webhook_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    验证Webhook签名
    
    Args:
        payload: 请求数据
        signature: 接收到的签名
        secret: 密钥
    
    Returns:
        签名是否有效
    """
    expected_signature = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(expected_signature, signature)


def create_download_webhook_data(space_id: str, version: str, ip_address: str) -> Dict[str, Any]:
    """
    创建下载事件的Webhook数据
    """
    return {
        "space_id": space_id,
        "version": version,
        "ip_address": ip_address,
        "event_time": datetime.utcnow().isoformat() + "Z"
    }


def create_version_publish_webhook_data(space_id: str, version: str) -> Dict[str, Any]:
    """
    创建版本发布事件的Webhook数据
    """
    return {
        "space_id": space_id,
        "version": version,
        "event_time": datetime.utcnow().isoformat() + "Z"
    }


def create_space_update_webhook_data(space_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建软件空间更新事件的Webhook数据
    """
    return {
        "space_id": space_id,
        "changes": changes,
        "event_time": datetime.utcnow().isoformat() + "Z"
    }


def create_version_update_webhook_data(space_id: str, version: str, changes: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建版本更新事件的Webhook数据
    """
    return {
        "space_id": space_id,
        "version": version,
        "changes": changes,
        "event_time": datetime.utcnow().isoformat() + "Z"
    }