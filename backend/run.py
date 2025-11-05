#!/usr/bin/env python
import os
import sys
import click
from flask_migrate import upgrade
from app import create_app, db
from app.utils.auth import create_user
from app.models.user import User
from app.models.software import SoftwareSpace, SoftwareVersion
from app.models.statistics import DownloadRecord, WebhookLog
from app.database import init_db as init_database, reset_db as reset_database
from sqlalchemy.exc import OperationalError


# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG', 'default'))


@app.shell_context_processor
def make_shell_context():
    """为Flask shell添加上下文"""
    return dict(
        db=db,
        User=User,
        SoftwareSpace=SoftwareSpace,
        SoftwareVersion=SoftwareVersion,
        DownloadRecord=DownloadRecord,
        WebhookLog=WebhookLog
    )


@app.cli.command()
@click.option('--username', prompt=True, help='管理员用户名')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='管理员密码')
@click.option('--email', default=None, help='管理员邮箱')
def init_admin(username, password, email):
    """初始化管理员账户"""
    # 检查是否已经存在管理员
    try:
        admin_exists = User.query.filter_by(role='admin').first()
    except OperationalError:
        # 如果表不存在，则自动创建所有表以便继续初始化（仅在第一次使用时）
        click.echo('检测到数据库表不存在，正在初始化数据库...')
        db.create_all()
        admin_exists = None

    if admin_exists:
        click.echo('管理员已存在，无法重复创建', err=True)
        sys.exit(1)
    
    # 创建管理员
    user, message = create_user(username, password, email, 'admin')
    
    if user:
        click.echo(f'管理员创建成功: {user.username}')
    else:
        click.echo(f'管理员创建失败: {message}', err=True)
        sys.exit(1)


@app.cli.command()
def init_db():
    """初始化数据库"""
    click.echo('正在初始化数据库...')
    init_database()
    click.echo('数据库初始化完成')


@app.cli.command()
def reset_db():
    """重置数据库（谨慎使用）"""
    if click.confirm('确定要重置数据库吗？所有数据将被删除！'):
        click.echo('正在重置数据库...')
        reset_database()
        click.echo('数据库重置完成')
    else:
        click.echo('操作已取消')


@app.cli.command()
def upgrade_db():
    """升级数据库"""
    click.echo('正在升级数据库...')
    upgrade()
    click.echo('数据库升级完成')


if __name__ == '__main__':
    # 如果通过命令行传入参数（例如 init-admin），把执行权交给 Flask CLI，这样 @app.cli.command 注册的命令可以正常工作。
    import sys
    if len(sys.argv) > 1:
        # 兼容用户可能输入的下划线命令名（如 init_admin）
        if '_' in sys.argv[1]:
            sys.argv[1] = sys.argv[1].replace('_', '-')

        from flask.cli import main as flask_cli_main
        flask_cli_main()
    else:
        # 获取配置并以传统方式直接运行应用（无 CLI 参数时）
        debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        https_enabled = os.getenv('HTTPS_ENABLED', 'False').lower() == 'true'
        
        # 运行应用
        if https_enabled:
            ssl_cert = os.getenv('SSL_CERT_PATH', 'certs/localhost.crt')
            ssl_key = os.getenv('SSL_KEY_PATH', 'certs/localhost.key')
            
            if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
                app.run(
                    debug=debug,
                    host=host,
                    port=port,
                    ssl_context=(ssl_cert, ssl_key)
                )
            else:
                print(f"SSL证书文件不存在: {ssl_cert} 或 {ssl_key}")
                print("以HTTP模式启动...")
                app.run(
                    debug=debug,
                    host=host,
                    port=port
                )
        else:
            app.run(
                debug=debug,
                host=host,
                port=port
            )