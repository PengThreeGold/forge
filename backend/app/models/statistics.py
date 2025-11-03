from datetime import datetime
from app import db


class DownloadRecord(db.Model):
    """下载记录模型"""
    __tablename__ = 'download_records'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('software_versions.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('software_spaces.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    download_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, version_id, space_id, ip_address, user_agent=None):
        self.version_id = version_id
        self.space_id = space_id
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'version_id': self.version_id,
            'space_id': self.space_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'download_time': self.download_time.isoformat() if self.download_time else None
        }
    
    def __repr__(self):
        return f'<DownloadRecord {self.id}>'


class WebhookLog(db.Model):
    """回调日志模型"""
    __tablename__ = 'webhook_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('software_spaces.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    response_status = db.Column(db.Integer, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, space_id, event_type, payload=None, response_status=None, response_body=None):
        self.space_id = space_id
        self.event_type = event_type
        self.payload = payload
        self.response_status = response_status
        self.response_body = response_body
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'space_id': self.space_id,
            'event_type': self.event_type,
            'payload': self.payload,
            'response_status': self.response_status,
            'response_body': self.response_body,
            'attempt_time': self.attempt_time.isoformat() if self.attempt_time else None
        }
    
    def __repr__(self):
        return f'<WebhookLog {self.id}>'