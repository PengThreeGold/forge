"""
HTTPS 配置模块

此模块包含与HTTPS相关的配置，用于在生产环境中启用HTTPS。
"""

import os
from pathlib import Path

# HTTPS 配置
HTTPS_ENABLED = os.getenv('HTTPS_ENABLED', 'False').lower() == 'true'

# SSL证书配置
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', 'certs/localhost.crt')
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', 'certs/localhost.key')

# 确保证书路径是绝对路径
if not os.path.isabs(SSL_CERT_PATH):
    SSL_CERT_PATH = os.path.join(Path(__file__).parent.parent.parent, 'nginx', SSL_CERT_PATH)

if not os.path.isabs(SSL_KEY_PATH):
    SSL_KEY_PATH = os.path.join(Path(__file__).parent.parent.parent, 'nginx', SSL_KEY_PATH)

# SSL 上下文配置
SSL_CONTEXT = None

if HTTPS_ENABLED:
    try:
        import ssl
        SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        SSL_CONTEXT.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)
    except Exception as e:
        print(f"警告: 无法加载SSL证书: {e}")
        print("请确保证书文件存在并且路径正确。")
        HTTPS_ENABLED = False