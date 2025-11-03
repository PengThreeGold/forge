from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord, WebhookLog
from app import db


class StatisticsService:
    """统计服务类"""
    
    @staticmethod
    def get_overview():
        """获取统计概览"""
        # 软件空间总数
        spaces_count = SoftwareSpace.query.count()
        
        # 软件版本总数
        versions_count = SoftwareVersion.query.count()
        
        # 已发布版本数
        published_versions_count = SoftwareVersion.query.filter_by(is_published=True).count()
        
        # 总下载次数
        total_downloads = DownloadRecord.query.count()
        
        # 最近7天下载次数
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_downloads = DownloadRecord.query.filter(
            DownloadRecord.download_time >= seven_days_ago
        ).count()
        
        # 最近30天下载次数
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_downloads = DownloadRecord.query.filter(
            DownloadRecord.download_time >= thirty_days_ago
        ).count()
        
        # 按IP统计的独立下载用户数
        unique_ips = DownloadRecord.query.with_entities(
            DownloadRecord.ip_address
        ).distinct().count()
        
        # 按软件空间统计下载次数
        spaces_downloads = db.session.query(
            SoftwareSpace.name,
            func.count(DownloadRecord.id).label('downloads')
        ).join(
            DownloadRecord, SoftwareSpace.id == DownloadRecord.space_id
        ).group_by(
            SoftwareSpace.id, SoftwareSpace.name
        ).order_by(
            desc('downloads')
        ).limit(10).all()
        
        spaces_downloads_data = [
            {
                'name': space.name,
                'downloads': downloads
            }
            for space, downloads in spaces_downloads
        ]
        
        # 按版本统计下载次数
        versions_downloads = db.session.query(
            SoftwareSpace.name.label('space_name'),
            SoftwareVersion.version,
            func.count(DownloadRecord.id).label('downloads')
        ).join(
            SoftwareVersion, DownloadRecord.version_id == SoftwareVersion.id
        ).join(
            SoftwareSpace, SoftwareVersion.space_id == SoftwareSpace.id
        ).group_by(
            SoftwareSpace.id, SoftwareSpace.name, SoftwareVersion.id, SoftwareVersion.version
        ).order_by(
            desc('downloads')
        ).limit(10).all()
        
        versions_downloads_data = [
            {
                'space_name': space_name,
                'version': version,
                'downloads': downloads
            }
            for space_name, version, downloads in versions_downloads
        ]
        
        # 最近下载记录
        recent_downloads_records = DownloadRecord.query.order_by(
            DownloadRecord.download_time.desc()
        ).limit(10).all()
        
        recent_downloads_data = [
            {
                'id': record.id,
                'space_name': record.space.name,
                'version': record.version.version,
                'ip_address': record.ip_address,
                'download_time': record.download_time.isoformat() if record.download_time else None
            }
            for record in recent_downloads_records
        ]
        
        return {
            'spaces_count': spaces_count,
            'versions_count': versions_count,
            'published_versions_count': published_versions_count,
            'total_downloads': total_downloads,
            'recent_downloads': recent_downloads,
            'monthly_downloads': monthly_downloads,
            'unique_ips': unique_ips,
            'spaces_downloads': spaces_downloads_data,
            'versions_downloads': versions_downloads_data,
            'recent_downloads': recent_downloads_data
        }
    
    @staticmethod
    def get_downloads(page=1, per_page=20, space_id=None, version_id=None, start_date=None, end_date=None):
        """获取下载统计"""
        # 构建查询
        query = DownloadRecord.query
        
        if space_id:
            query = query.filter(DownloadRecord.space_id == space_id)
        
        if version_id:
            query = query.filter(DownloadRecord.version_id == version_id)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(DownloadRecord.download_time >= start_date)
            except ValueError:
                return None, "开始日期格式不正确，请使用YYYY-MM-DD格式"
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 结束日期加一天，以便包含结束日期当天的数据
                end_date = end_date + timedelta(days=1)
                query = query.filter(DownloadRecord.download_time < end_date)
            except ValueError:
                return None, "结束日期格式不正确，请使用YYYY-MM-DD格式"
        
        # 分页查询
        pagination = query.order_by(
            DownloadRecord.download_time.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 格式化结果
        downloads_data = [
            {
                'id': record.id,
                'space_name': record.space.name,
                'version': record.version.version,
                'ip_address': record.ip_address,
                'user_agent': record.user_agent,
                'download_time': record.download_time.isoformat() if record.download_time else None
            }
            for record in pagination.items
        ]
        
        return {
            'downloads': downloads_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }, "获取成功"
    
    @staticmethod
    def get_downloads_timeline(days=30, space_id=None):
        """获取下载时间线统计"""
        # 限制查询天数，最多365天
        days = min(days, 365)
        
        # 计算开始日期
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 构建查询
        query = DownloadRecord.query.filter(
            DownloadRecord.download_time >= start_date
        )
        
        if space_id:
            query = query.filter(DownloadRecord.space_id == space_id)
        
        # 按天统计下载次数
        daily_downloads = db.session.query(
            func.date(DownloadRecord.download_time).label('date'),
            func.count(DownloadRecord.id).label('downloads')
        ).filter(
            DownloadRecord.download_time >= start_date
        )
        
        if space_id:
            daily_downloads = daily_downloads.filter(DownloadRecord.space_id == space_id)
        
        daily_downloads = daily_downloads.group_by(
            func.date(DownloadRecord.download_time)
        ).order_by(
            func.date(DownloadRecord.download_time)
        ).all()
        
        # 格式化结果
        timeline_data = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'downloads': downloads
            }
            for date, downloads in daily_downloads
        ]
        
        # 生成完整的时间线，填充缺失的日期
        complete_timeline = []
        current_date = start_date.date()
        end_date = datetime.utcnow().date()
        
        timeline_dict = {item['date']: item['downloads'] for item in timeline_data}
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            complete_timeline.append({
                'date': date_str,
                'downloads': timeline_dict.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return {
            'timeline': complete_timeline,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    
    @staticmethod
    def get_space_statistics(space_id):
        """获取指定软件空间的统计信息"""
        space = SoftwareSpace.query.get(space_id)
        
        if not space:
            return None, "软件空间不存在"
        
        # 软件空间基本信息
        space_info = {
            'id': space.id,
            'name': space.name,
            'description': space.description,
            'author': space.author,
            'created_at': space.created_at.isoformat() if space.created_at else None,
            'versions_count': space.versions.count(),
            'downloads_count': space.download_records.count()
        }
        
        # 各版本下载次数
        versions_downloads = db.session.query(
            SoftwareVersion.version,
            SoftwareVersion.is_published,
            func.count(DownloadRecord.id).label('downloads')
        ).join(
            DownloadRecord, SoftwareVersion.id == DownloadRecord.version_id
        ).filter(
            SoftwareVersion.space_id == space_id
        ).group_by(
            SoftwareVersion.id, SoftwareVersion.version, SoftwareVersion.is_published
        ).order_by(
            desc('downloads')
        ).all()
        
        versions_downloads_data = [
            {
                'version': version,
                'is_published': is_published,
                'downloads': downloads
            }
            for version, is_published, downloads in versions_downloads
        ]
        
        # 最近下载记录
        recent_downloads = DownloadRecord.query.filter_by(
            space_id=space_id
        ).order_by(
            DownloadRecord.download_time.desc()
        ).limit(10).all()
        
        recent_downloads_data = [
            {
                'id': record.id,
                'version': record.version.version,
                'ip_address': record.ip_address,
                'user_agent': record.user_agent,
                'download_time': record.download_time.isoformat() if record.download_time else None
            }
            for record in recent_downloads
        ]
        
        # 最近30天下载趋势
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_downloads = db.session.query(
            func.date(DownloadRecord.download_time).label('date'),
            func.count(DownloadRecord.id).label('downloads')
        ).filter(
            and_(
                DownloadRecord.space_id == space_id,
                DownloadRecord.download_time >= thirty_days_ago
            )
        ).group_by(
            func.date(DownloadRecord.download_time)
        ).order_by(
            func.date(DownloadRecord.download_time)
        ).all()
        
        # 格式化结果
        timeline_data = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'downloads': downloads
            }
            for date, downloads in daily_downloads
        ]
        
        # 生成完整的时间线，填充缺失的日期
        complete_timeline = []
        current_date = thirty_days_ago.date()
        end_date = datetime.utcnow().date()
        
        timeline_dict = {item['date']: item['downloads'] for item in timeline_data}
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            complete_timeline.append({
                'date': date_str,
                'downloads': timeline_dict.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return {
            'space_info': space_info,
            'versions_downloads': versions_downloads_data,
            'recent_downloads': recent_downloads_data,
            'timeline': complete_timeline
        }
    
    @staticmethod
    def get_webhooks(page=1, per_page=20, space_id=None):
        """获取Webhook日志列表"""
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
        
        return {
            'webhooks': webhooks_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_webhook(log_id):
        """获取Webhook日志详情"""
        log = WebhookLog.query.get(log_id)
        
        if not log:
            return None, "Webhook日志不存在"
        
        return {
            'id': log.id,
            'space_name': log.space.name,
            'event_type': log.event_type,
            'payload': log.payload,
            'response_status': log.response_status,
            'response_body': log.response_body,
            'attempt_time': log.attempt_time.isoformat() if log.attempt_time else None
        }