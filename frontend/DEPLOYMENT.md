# Forge 软件发布管理平台 - 部署指南

本文档提供了 Forge 软件发布管理平台的详细部署指南，包括开发环境、生产环境和 Docker 部署方式。

## 目录

- [部署概述](#部署概述)
- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [HTTPS 配置](#https-配置)
- [数据库配置](#数据库配置)
- [Nginx 配置](#nginx-配置)
- [系统监控与日志](#系统监控与日志)
- [常见问题与解决方案](#常见问题与解决方案)

## 部署概述

Forge 软件发布管理平台支持多种部署方式，包括本地开发环境部署、生产环境部署和 Docker 容器化部署。本文档将详细介绍各种部署方式的步骤和注意事项。

### 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                     用户访问层                                │
├─────────────────────────────────────────────────────────────┤
│                        Nginx                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │   HTTPS (443)      │  │     HTTP (80)              │   │
│  └─────────┬─────────┘  └──────────────┬──────────────┘   │
│            │                              │                  │
│  ┌─────────▼─────────┐  ┌──────────────▼──────────────┐   │
│  │   前端应用 (Vue)   │  │     后端 API (Flask)       │   │
│  │   Port: 8080       │  │     Port: 5000             │   │
│  └───────────────────┘  └─────────────────────────────┘   │
│            │                              │                  │
│  ┌─────────▼─────────┐  ┌──────────────▼──────────────┐   │
│  │   静态文件服务      │  │     数据库 (SQLite/PG/MySQL)│   │
│  └───────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 环境要求

### 系统要求

- **操作系统**: Linux (Ubuntu 20.04+/CentOS 7+), Windows 10, macOS 10.15+
- **内存**: 最少 2GB RAM，推荐 4GB 以上
- **存储**: 最少 10GB 可用空间，推荐 50GB 以上
- **网络**: 稳定的互联网连接（用于下载依赖包）

### 软件要求

- **Python**: 3.8+
- **Node.js**: 16+
- **Git**: 最新版本
- **Docker**: 20.10+ (可选，用于容器化部署)
- **Docker Compose**: 1.29+ (可选，用于容器化部署)
- **Nginx**: 1.18+ (可选，用于生产环境反向代理)

### 数据库要求

- **开发环境**: SQLite (默认)
- **生产环境**: PostgreSQL 12+ 或 MySQL 8.0+ (推荐)

## 开发环境部署

### 前端部署

1. **克隆项目**

```bash
git clone https://github.com/your-username/forge.git
cd forge
```

2. **安装 Node.js 依赖**

```bash
cd frontend
npm install
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

`.env` 文件示例：

```
VUE_APP_API_BASE_URL=http://localhost:5000/api
VUE_APP_TITLE=Forge 软件发布管理平台
VUE_APP_VERSION=1.0.0
```

4. **启动开发服务器**

```bash
npm run serve
```

访问 http://localhost:8080 查看前端应用。

### 后端部署

1. **创建 Python 虚拟环境**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

2. **安装 Python 依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

`.env` 文件示例：

```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800
DATABASE_URL=sqlite:///forge.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=1073741824
```

4. **初始化数据库**

```bash
python run.py db-init
```

5. **创建管理员账户**

```bash
python run.py create-admin
```

按照提示输入管理员用户名、密码和邮箱。

6. **启动开发服务器**

```bash
python run.py run
```

访问 http://localhost:5000/api 查看后端 API。

## 生产环境部署

### 前端构建与部署

1. **构建生产版本**

```bash
cd frontend
npm install
npm run build
```

构建完成后，`dist` 目录将包含生产环境的静态文件。

2. **部署静态文件**

将 `dist` 目录中的文件复制到 Web 服务器的静态文件目录，例如：

```bash
sudo cp -r dist/* /var/www/forge/
```

### 后端部署

1. **安装系统依赖**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip nginx
```

2. **创建应用目录**

```bash
sudo mkdir -p /opt/forge
sudo chown $USER:$USER /opt/forge
```

3. **克隆项目**

```bash
git clone https://github.com/your-username/forge.git /opt/forge
cd /opt/forge
```

4. **创建 Python 虚拟环境**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

5. **安装 Python 依赖**

```bash
pip install -r requirements.txt
pip install gunicorn
```

6. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

生产环境 `.env` 文件示例：

```
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800
DATABASE_URL=postgresql://username:password@localhost/forge_db
UPLOAD_FOLDER=/opt/forge/uploads
MAX_CONTENT_LENGTH=1073741824
```

7. **初始化数据库**

```bash
python run.py db-init
```

8. **创建管理员账户**

```bash
python run.py create-admin
```

9. **创建 Gunicorn 服务文件**

```bash
sudo nano /etc/systemd/system/forge.service
```

添加以下内容：

```ini
[Unit]
Description=Forge API Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/forge/backend
Environment="PATH=/opt/forge/backend/venv/bin"
ExecStart=/opt/forge/backend/venv/bin/gunicorn --workers 3 --bind unix:forge.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

10. **启动并启用 Gunicorn 服务**

```bash
sudo systemctl start forge
sudo systemctl enable forge
```

### Nginx 配置

1. **创建 Nginx 配置文件**

```bash
sudo nano /etc/nginx/sites-available/forge
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/forge;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://unix:/opt/forge/backend/forge.sock;
        include proxy_params;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /opt/forge/uploads;
    }

    location /public {
        alias /opt/forge/backend/public;
    }
}
```

2. **启用配置**

```bash
sudo ln -s /etc/nginx/sites-available/forge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Docker 部署

### 使用 Docker Compose

1. **克隆项目**

```bash
git clone https://github.com/your-username/forge.git
cd forge
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

`.env` 文件示例：

```
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your-docker-secret-key
JWT_SECRET_KEY=your-docker-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800
DATABASE_URL=postgresql://forge:forge_password@db:5432/forge_db
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=1073741824
POSTGRES_DB=forge_db
POSTGRES_USER=forge
POSTGRES_PASSWORD=forge_password
```

3. **启动服务**

```bash
docker-compose up -d
```

这将启动以下服务：
- `frontend`: 前端 Vue 应用
- `backend`: 后端 Flask 应用
- `db`: PostgreSQL 数据库
- `nginx`: Nginx 反向代理

4. **初始化数据库**

```bash
docker-compose exec backend python run.py db-init
```

5. **创建管理员账户**

```bash
docker-compose exec backend python run.py create-admin
```

6. **查看服务状态**

```bash
docker-compose ps
```

7. **查看日志**

```bash
docker-compose logs -f
```

### 使用 Docker Swarm

1. **初始化 Swarm**

```bash
docker swarm init
```

2. **创建 Docker 密钥**

```bash
echo "your-secret-key" | docker secret create forge_secret_key -
echo "your-jwt-secret-key" | docker secret create forge_jwt_secret_key -
echo "forge_password" | docker secret create forge_db_password -
```

3. **部署 Stack**

```bash
docker stack deploy -c docker-compose.yml forge
```

4. **查看服务状态**

```bash
docker service ls
```

5. **查看日志**

```bash
docker service logs -f forge_backend
```

## HTTPS 配置

### 使用 Let's Encrypt (推荐)

1. **安装 Certbot**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

2. **获取 SSL 证书**

```bash
sudo certbot --nginx -d your-domain.com
```

按照提示完成证书申请过程。

3. **自动续期**

```bash
sudo crontab -e
```

添加以下内容：

```
0 12 * * * /usr/bin/certbot renew --quiet
```

### 使用自签名证书 (开发环境)

1. **生成自签名证书**

```bash
mkdir -p nginx/ssl
cd nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout forge.key -out forge.crt
```

2. **配置 Nginx**

编辑 Nginx 配置文件，添加 SSL 配置：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/forge.crt;
    ssl_certificate_key /path/to/forge.key;

    location / {
        root /var/www/forge;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://unix:/opt/forge/backend/forge.sock;
        include proxy_params;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /opt/forge/uploads;
    }

    location /public {
        alias /opt/forge/backend/public;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}
```

3. **重启 Nginx**

```bash
sudo systemctl restart nginx
```

### 使用 Docker 和 Let's Encrypt

1. **创建 Docker Compose 文件**

```bash
cp docker-compose.yml docker-compose.ssl.yml
```

2. **编辑 Docker Compose 文件**

添加 Let's Encrypt 服务：

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - ./frontend/dist:/usr/share/nginx/html
      - ./backend/uploads:/usr/share/nginx/uploads
    depends_on:
      - frontend
      - backend
    networks:
      - forge-network

  certbot:
    image: certbot/certbot
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - nginx
    networks:
      - forge-network

  # 其他服务保持不变...

volumes:
  certbot-etc:
  certbot-var:

networks:
  forge-network:
    driver: bridge
```

3. **获取 SSL 证书**

```bash
docker-compose -f docker-compose.ssl.yml run --rm certbot certonly --webroot --webroot-path /usr/share/nginx/html -d your-domain.com
```

4. **更新 Nginx 配置**

编辑 `nginx/nginx.conf`，添加 SSL 配置。

5. **重启服务**

```bash
docker-compose -f docker-compose.ssl.yml up -d --force-recreate
```

## 数据库配置

### SQLite (开发环境)

SQLite 是默认的数据库，无需额外配置。数据库文件位于 `backend/forge.db`。

### PostgreSQL (生产环境)

1. **安装 PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. **创建数据库和用户**

```bash
sudo -u postgres psql
```

在 PostgreSQL 提示符下执行：

```sql
CREATE DATABASE forge_db;
CREATE USER forge WITH ENCRYPTED PASSWORD 'forge_password';
GRANT ALL PRIVILEGES ON DATABASE forge_db TO forge;
\q
```

3. **配置后端**

编辑 `.env` 文件，设置数据库连接字符串：

```
DATABASE_URL=postgresql://forge:forge_password@localhost:5432/forge_db
```

4. **初始化数据库**

```bash
cd backend
source venv/bin/activate
python run.py db-init
```

### MySQL (生产环境)

1. **安装 MySQL**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

2. **安全配置**

```bash
sudo mysql_secure_installation
```

3. **创建数据库和用户**

```bash
sudo mysql -u root -p
```

在 MySQL 提示符下执行：

```sql
CREATE DATABASE forge_db;
CREATE USER 'forge'@'localhost' IDENTIFIED BY 'forge_password';
GRANT ALL PRIVILEGES ON forge_db.* TO 'forge'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

4. **配置后端**

编辑 `.env` 文件，设置数据库连接字符串：

```
DATABASE_URL=mysql+pymysql://forge:forge_password@localhost:3306/forge_db
```

5. **安装 MySQL 驱动**

```bash
cd backend
source venv/bin/activate
pip install PyMySQL
```

6. **初始化数据库**

```bash
python run.py db-init
```

### 数据库备份与恢复

#### PostgreSQL

**备份**:

```bash
sudo -u postgres pg_dump forge_db > forge_db_backup.sql
```

**恢复**:

```bash
sudo -u postgres psql forge_db < forge_db_backup.sql
```

#### MySQL

**备份**:

```bash
mysqldump -u forge -p forge_db > forge_db_backup.sql
```

**恢复**:

```bash
mysql -u forge -p forge_db < forge_db_backup.sql
```

## Nginx 配置

### 基本配置

```nginx
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Gzip 配置
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate max-age=0 auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # 上游服务器配置
    upstream forge_backend {
        server unix:/opt/forge/backend/forge.sock;
    }

    # HTTP 服务器配置
    server {
        listen 80;
        server_name your-domain.com;

        # 重定向到 HTTPS
        return 301 https://$host$request_uri;
    }

    # HTTPS 服务器配置
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 配置
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1d;
        ssl_session_tickets off;

        # HSTS 配置
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 静态文件服务
        location / {
            root /var/www/forge;
            try_files $uri $uri/ /index.html;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API 代理
        location /api {
            proxy_pass http://forge_backend;
            include proxy_params;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # 文件上传目录
        location /uploads {
            alias /opt/forge/uploads;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 公开资源目录
        location /public {
            alias /opt/forge/backend/public;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 性能优化

1. **调整 worker 进程数**

```nginx
worker_processes auto;
worker_rlimit_nofile 100000;
```

2. **调整连接数**

```nginx
events {
    worker_connections 4096;
    multi_accept on;
    use epoll;
}
```

3. **调整缓冲区大小**

```nginx
http {
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    client_max_body_size 1G;
    large_client_header_buffers 2 1k;
}
```

4. **启用 HTTP/2**

```nginx
listen 443 ssl http2;
```

5. **启用 Brotli 压缩**

```nginx
# 需要安装 nginx-brotli 模块
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

## 系统监控与日志

### 应用监控

1. **使用 Prometheus 和 Grafana**

```bash
# 安装 Prometheus
docker run -d --name prometheus -p 9090:9090 -v /opt/forge/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# 安装 Grafana
docker run -d --name grafana -p 3000:3000 grafana/grafana
```

2. **配置 Prometheus**

创建 `prometheus.yml` 文件：

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'forge'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

3. **集成 Prometheus 到 Flask 应用**

安装依赖：

```bash
pip install prometheus-client
```

在 Flask 应用中添加：

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# 定义指标
REQUEST_COUNT = Counter('forge_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('forge_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('forge_active_users', 'Active users')

# 在请求处理前
@app.before_request
def before_request():
    request.start_time = time.time()

# 在请求处理后
@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.endpoint).inc()
    REQUEST_DURATION.observe(request_latency)
    return response

# 添加指标端点
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
```

### 日志管理

1. **使用 ELK Stack**

```bash
# 安装 Elasticsearch
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.0

# 安装 Logstash
docker run -d --name logstash -p 5044:5044 --link elasticsearch:elasticsearch -v /opt/forge/logstash.conf:/usr/share/logstash/pipeline/logstash.conf logstash:7.17.0

# 安装 Kibana
docker run -d --name kibana -p 5601:5601 --link elasticsearch:elasticsearch kibana:7.17.0
```

2. **配置 Logstash**

创建 `logstash.conf` 文件：

```conf
input {
  beats {
    port => 5044
  }
}

filter {
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "forge-logs-%{+YYYY.MM.dd}"
  }
}
```

3. **配置 Filebeat**

安装 Filebeat：

```bash
sudo apt install filebeat
```

配置 Filebeat (`/etc/filebeat/filebeat.yml`):

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/nginx/access.log
    - /var/log/nginx/error.log
    - /opt/forge/logs/*.log

output.logstash:
  hosts: ["localhost:5044"]
```

启动 Filebeat：

```bash
sudo systemctl start filebeat
sudo systemctl enable filebeat
```

### 告警配置

1. **使用 Alertmanager**

```bash
docker run -d --name alertmanager -p 9093:9093 -v /opt/forge/alertmanager.yml:/etc/alertmanager/alertmanager.yml prom/alertmanager
```

2. **配置 Alertmanager**

创建 `alertmanager.yml` 文件：

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@example.com'
```

## 常见问题与解决方案

### 部署问题

#### 问题 1: 前端无法访问后端 API

**症状**: 前端显示 "Network Error" 或 "CORS Error"

**解决方案**:

1. 检查后端服务是否正常运行:

```bash
curl http://localhost:5000/api/health
```

2. 检查 CORS 配置:

确保后端已正确配置 Flask-CORS:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

3. 检查前端 API 配置:

检查前端 `.env` 文件中的 `VUE_APP_API_BASE_URL` 配置是否正确。

#### 问题 2: 数据库连接失败

**症状**: 后端显示数据库连接错误

**解决方案**:

1. 检查数据库服务是否运行:

```bash
# PostgreSQL
sudo systemctl status postgresql

# MySQL
sudo systemctl status mysqld
```

2. 检查数据库连接字符串:

确保 `.env` 文件中的 `DATABASE_URL` 格式正确。

3. 检查数据库用户权限:

确保数据库用户具有足够的权限访问数据库。

#### 问题 3: 文件上传失败

**症状**: 上传文件时显示错误

**解决方案**:

1. 检查上传目录权限:

```bash
sudo chown -R www-data:www-data /opt/forge/uploads
sudo chmod -R 755 /opt/forge/uploads
```

2. 检查文件大小限制:

确保 `.env` 文件中的 `MAX_CONTENT_LENGTH` 配置足够大。

3. 检查 Nginx 配置:

确保 Nginx 配置中的 `client_max_body_size` 足够大:

```nginx
client_max_body_size 1G;
```

### HTTPS 问题

#### 问题 1: SSL 证书错误

**症状**: 浏览器显示 SSL 证书警告

**解决方案**:

1. 检查证书是否有效:

```bash
openssl x509 -in forge.crt -text -noout
```

2. 检查证书链是否完整:

确保服务器配置包含完整的证书链。

3. 检查域名匹配:

确保证书中的域名与访问的域名匹配。

#### 问题 2: 混合内容警告

**症状**: 浏览器显示混合内容警告

**解决方案**:

1. 检查资源 URL:

确保所有资源都使用 HTTPS 协议。

2. 更新 Nginx 配置:

添加 `Content-Security-Policy` 头:

```nginx
add_header Content-Security-Policy "upgrade-insecure-requests" always;
```

3. 更新应用配置:

确保应用中的资源 URL 使用 HTTPS 协议。

### 性能问题

#### 问题 1: 响应时间过长

**症状**: API 响应时间过长

**解决方案**:

1. 检查数据库查询性能:

使用 `EXPLAIN ANALYZE` 分析慢查询。

2. 优化数据库索引:

为常用查询字段添加索引。

3. 使用缓存:

为频繁访问的数据添加缓存:

```python
from flask_caching import Cache

cache = Cache(app)

@app.route('/api/software')
@cache.cached(timeout=60)
def get_software():
    # 从数据库获取软件列表
    pass
```

4. 增加工作进程:

增加 Gunicorn 工作进程数:

```ini
ExecStart=/opt/forge/backend/venv/bin/gunicorn --workers 5 --bind unix:forge.sock -m 007 run:app
```

#### 问题 2: 内存使用过高

**症状**: 服务器内存使用率过高

**解决方案**:

1. 检查内存使用:

```bash
ps aux --sort=-%mem | head
```

2. 优化应用代码:

检查是否有内存泄漏。

3. 调整工作进程数:

减少 Gunicorn 工作进程数。

4. 使用内存缓存:

使用 Redis 等外部缓存。

### 安全问题

#### 问题 1: 未授权访问

**症状**: 未登录用户可以访问受限资源

**解决方案**:

1. 检查认证中间件:

确保所有需要认证的路由都添加了认证装饰器:

```python
from app.utils.auth import token_required

@app.route('/api/admin')
@token_required
def admin_route():
    # 管理员路由
    pass
```

2. 检查权限控制:

确保实施了适当的权限控制。

3. 检查路由配置:

确保敏感路由不在公开的路由组中。

#### 问题 2: 文件上传安全

**症状**: 恶意文件上传风险

**解决方案**:

1. 检查文件类型:

限制允许上传的文件类型:

```python
ALLOWED_EXTENSIONS = {'exe', 'msi', 'dmg', 'pkg', 'deb', 'rpm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

2. 检查文件内容:

使用文件类型检查工具验证文件内容。

3. 使用安全文件名:

生成安全的文件名:

```python
import os
import uuid

def secure_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4()}.{ext}"
```

4. 限制文件大小:

限制上传文件的最大大小。

通过以上部署指南，您应该能够成功部署 Forge 软件发布管理平台。如果您在部署过程中遇到任何问题，请参考常见问题与解决方案部分，或联系技术支持。