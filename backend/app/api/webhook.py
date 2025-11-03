import requests
import json
import hashlib
import hmac
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response, admin_required
from app.models.user import User
from app.models.software import SoftwareSpace
from app.models.statistics import WebhookLog, DownloadRecord
from app import db
from typing import Any

# 类型提示，避免pylance错误
session: Any = db.session

webhook_bp = Blueprint('webhook', __name__)


def verify_webhook_signature(payload, signature, secret):
    """验证Webhook签名"""
    if not signature or not secret:
        return False
    
    # 计算HMAC签名
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # 比较签名
    return hmac.compare_digest(computed_signature, signature)


def trigger_webhook(space, event_type, data):
    """触发Webhook回调"""
    if not space.webhook_url:
        return False, "未配置Webhook URL"
    
    # 准备请求数据
    payload = {
        'event': event_type,
        'timestamp': data.get('timestamp'),
        'data': data
    }
    
    # 序列化为JSON
    json_payload = json.dumps(payload)
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Forge-Webhook/1.0'
    }
    
    # 如果有密钥，添加签名
    if space.webhook_secret:
        signature = hmac.new(
            space.webhook_secret.encode('utf-8'),
            json_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        headers['X-Forge-Signature'] = f'sha256={signature}'
    
    try:
        # 发送请求
        response = requests.post(
            space.webhook_url,
            data=json_payload,
            headers=headers,
            timeout=10
        )
        
        # 记录日志
        webhook_log = WebhookLog(
            space_id=space.id,
            event_type=event_type,
            payload=json_payload,
            response_status=response.status_code,
            response_body=response.text[:1000]  # 限制响应体长度
        )
        
        session.add(webhook_log)
        session.commit()
        
        # 返回结果
        if response.status_code < 400:
            return True, "Webhook回调成功"
        else:
            return False, f"Webhook回调失败，状态码: {response.status_code}"
    
    except Exception as e:
        # 记录错误日志
        webhook_log = WebhookLog(
            space_id=space.id,
            event_type=event_type,
            payload=json_payload,
            response_status=0,
            response_body=str(e)[:1000]
        )
        
        session.add(webhook_log)
        session.commit()
        
        return False, f"Webhook回调异常: {str(e)}"


@webhook_bp.route('/webhooks', methods=['GET'])
@jwt_required()
@admin_required
def get_webhooks():
    """获取Webhook日志列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    space_id = request.args.get('space_id', type=int)
    
    # 构建查询
    query = WebhookLog.query
    
    if space_id:
        query = query.filter(WebhookLog.space_id == space_id)
    
    # 分页查询
    pagination = query.order_by(
        WebhookLog.attempt_time.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 格式化结果
    webhooks_data = [
        {
            'id': log.id,
            'space_name': log.space.name,
            'event_type': log.event_type,
            'response_status': log.response_status,
            'attempt_time': log.attempt_time.isoformat() if log.attempt_time else None
        }
        for log in pagination.items
    ]
    
    return success_response({
        'webhooks': webhooks_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@webhook_bp.route('/webhooks/<int:log_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_webhook(log_id):
    """获取Webhook日志详情"""
    log = WebhookLog.query.get_or_404(log_id)
    
    return success_response({
        'id': log.id,
        'space_name': log.space.name,
        'event_type': log.event_type,
        'payload': log.payload,
        'response_status': log.response_status,
        'response_body': log.response_body,
        'attempt_time': log.attempt_time.isoformat() if log.attempt_time else None
    })


@webhook_bp.route('/webhooks/retry/<int:log_id>', methods=['POST'])
@jwt_required()
@admin_required
def retry_webhook(log_id):
    """重试Webhook回调"""
    log = WebhookLog.query.get_or_404(log_id)
    
    # 解析原始载荷
    try:
        payload_data = json.loads(log.payload)
        event_type = payload_data.get('event')
        data = payload_data.get('data')
        
        if not event_type or not data:
            return error_response("无效的Webhook日志数据", 400)
        
        # 重新触发Webhook
        success, message = trigger_webhook(log.space, event_type, data)
        
        if success:
            return success_response(message=message)
        else:
            return error_response(message, 500)
    
    except Exception as e:
        return error_response(f"重试失败: {str(e)}", 500)


@webhook_bp.route('/webhooks/test/<int:space_id>', methods=['POST'])
@jwt_required()
@admin_required
def test_webhook(space_id):
    """测试Webhook回调"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
    if not space.webhook_url:
        return error_response("未配置Webhook URL", 400)
    
    # 准备测试数据
    from datetime import datetime
    test_data = {
        'message': '这是一个测试Webhook回调',
        'space_id': space.id,
        'space_name': space.name,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # 触发测试Webhook
    success, message = trigger_webhook(space, 'test', test_data)
    
    if success:
        return success_response(message=message)
    else:
        return error_response(message, 500)


# 下载事件Webhook处理器
def handle_download_event(download_record):
    """处理下载事件"""
    space = download_record.space
    version = download_record.version
    
    # 准备事件数据
    event_data = {
        'space_id': space.id,
        'space_name': space.name,
        'version_id': version.id,
        'version': version.version,
        'download_id': download_record.id,
        'ip_address': download_record.ip_address,
        'user_agent': download_record.user_agent,
        'download_time': download_record.download_time.isoformat() if download_record.download_time else None
    }
    
    # 触发Webhook
    trigger_webhook(space, 'download', event_data)


# 新版本发布事件Webhook处理器
def handle_version_publish_event(version):
    """处理新版本发布事件"""
    space = version.space
    
    # 准备事件数据
    event_data = {
        'space_id': space.id,
        'space_name': space.name,
        'version_id': version.id,
        'version': version.version,
        'publish_date': version.publish_date.isoformat() if version.publish_date else None,
        'release_note': version.release_note,
        'file_size': version.file_size
    }
    
    # 触发Webhook
    trigger_webhook(space, 'version_publish', event_data)