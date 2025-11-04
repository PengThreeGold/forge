from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.utils.response import success_response, error_response, admin_required
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord
from app import db
from typing import Any

# 类型提示，避免pylance错误
session: Any = db.session

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/statistics/overview', methods=['GET'])
@jwt_required()
@admin_required
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
    spaces_downloads = session.query(
        SoftwareSpace.name,
        func.count(DownloadRecord.id).label('downloads')
    ).join(
        DownloadRecord, SoftwareSpace.id == DownloadRecord.space_id
    ).group_by(
        SoftwareSpace.id, SoftwareSpace.name
    ).order_by(
        desc('downloads')
    ).limit(10).all()
    
    # 查询返回 (space_name, downloads) 的元组
    spaces_downloads_data = [
        {
            'name': space_name,
            'downloads': downloads
        }
        for space_name, downloads in spaces_downloads
    ]
    
    # 按版本统计下载次数
    versions_downloads = session.query(
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
    
    # recent_downloads 是最近7天的计数，recent_downloads_data 是最近的记录列表，避免字段名冲突
    return success_response({
        'spaces_count': spaces_count,
        'versions_count': versions_count,
        'published_versions_count': published_versions_count,
        'total_downloads': total_downloads,
        'recent_downloads_count': recent_downloads,
        'monthly_downloads': monthly_downloads,
        'unique_ips': unique_ips,
        'spaces_downloads': spaces_downloads_data,
        'versions_downloads': versions_downloads_data,
        'recent_downloads': recent_downloads_data
    })


@statistics_bp.route('/statistics/downloads', methods=['GET'])
@jwt_required()
@admin_required
def get_downloads():
    """获取下载统计"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    space_id = request.args.get('space_id', type=int)
    version_id = request.args.get('version_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
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
            return error_response("开始日期格式不正确，请使用YYYY-MM-DD格式", 400)
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # 结束日期加一天，以便包含结束日期当天的数据
            end_date = end_date + timedelta(days=1)
            query = query.filter(DownloadRecord.download_time < end_date)
        except ValueError:
            return error_response("结束日期格式不正确，请使用YYYY-MM-DD格式", 400)
    
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
    
    return success_response({
        'downloads': downloads_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@statistics_bp.route('/statistics/downloads/timeline', methods=['GET'])
@jwt_required()
@admin_required
def get_downloads_timeline():
    """获取下载时间线统计"""
    # 获取查询参数
    days = request.args.get('days', 30, type=int)
    space_id = request.args.get('space_id', type=int)
    
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
    daily_downloads = session.query(
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
    
    return success_response({
        'timeline': complete_timeline,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    })


@statistics_bp.route('/statistics/spaces/<int:space_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_space_statistics(space_id):
    """获取指定软件空间的统计信息"""
    space = SoftwareSpace.query.get_or_404(space_id)
    
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
    versions_downloads = session.query(
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
    
    daily_downloads = session.query(
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
    
    return success_response({
        'space_info': space_info,
        'versions_downloads': versions_downloads_data,
        'recent_downloads': recent_downloads_data,
        'timeline': complete_timeline
    })