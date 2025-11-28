# AuthHub 自建服务器部署指南

本指南将帮助你在自建服务器上部署 AuthHub 项目。

## 📋 目录

- [前置要求](#前置要求)
- [部署方式选择](#部署方式选择)
- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：源码部署](#方式二源码部署)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

## 前置要求

### 硬件要求
- **CPU**: 2核及以上
- **内存**: 4GB 及以上
- **硬盘**: 20GB 及以上
- **网络**: 公网IP或域名（用于飞书回调）

### 软件要求

#### Docker 部署方式
- Docker 20.10+
- Docker Compose 2.0+

#### 源码部署方式
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- UV (Python包管理器)
- pnpm (Node.js包管理器)

### 飞书配置
- 飞书开放平台企业自建应用
- 配置 OAuth 回调地址: `https://your-domain.com/api/auth/feishu/callback`

## 部署方式选择

```mermaid
graph TD
    A[开始部署] --> B{是否熟悉Docker?}
    B -->|是| C[Docker部署<br/>简单快速推荐]
    B -->|否| D{是否需要定制化?}
    D -->|是| E[源码部署<br/>灵活可控]
    D -->|否| C
    
    C --> F[准备环境变量]
    E --> G[安装依赖]
    
    F --> H[启动服务]
    G --> H
    
    H --> I[配置反向代理]
    I --> J[配置飞书回调]
    J --> K[部署完成]
    
    style C fill:#90EE90
    style E fill:#87CEEB
```

## 方式一：Docker 部署（推荐）

### 1. 准备工作

```bash
# 克隆项目
git clone https://github.com/your-org/AuthHub.git
cd AuthHub
```

### 2. 准备外部数据库

> **重要**: 此部署方式使用外部数据库，不在 Docker 容器中运行数据库。

#### PostgreSQL 准备

```bash
# 连接到你的 PostgreSQL 服务器
psql -U postgres -h your-db-host

# 创建数据库和用户
CREATE DATABASE authhub;
CREATE USER authhub WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE authhub TO authhub;
\q
```

#### Redis 准备

确保你的 Redis 服务器已配置密码：

```bash
# 编辑 redis.conf
requirepass your_redis_password

# 重启 Redis
sudo systemctl restart redis
```

### 3. 配置环境变量

创建 `.env.production` 文件（在项目根目录）：

```bash
# ==================== 应用配置 ====================
APP_NAME=AuthHub
DEBUG=false
HOST=0.0.0.0
PORT=8080

# ==================== 外部数据库配置 ====================
# PostgreSQL 连接 URL（使用外部数据库的实际地址）
# ⚠️ 不能使用 localhost，要使用服务器的实际 IP 或域名
DATABASE_URL=postgresql+asyncpg://authhub:your_strong_password@192.168.1.100:5432/authhub

# ==================== 外部 Redis 配置 ====================
# Redis 连接 URL（使用外部 Redis 的实际地址）
# ⚠️ 不能使用 localhost，要使用服务器的实际 IP 或域名
REDIS_URL=redis://:your_redis_password@192.168.1.100:6379/0

# ==================== JWT配置 ====================
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
# Docker环境下的路径
JWT_PRIVATE_KEY_PATH=/app/keys/private_key.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public_key.pem

# ==================== 飞书配置 ====================
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret

# ==================== CORS配置 ====================
# 生产环境请修改为实际域名
CORS_ORIGINS=["https://your-domain.com"]

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
```

**配置文件说明**：
- 开发环境：使用项目根目录的 `.env` 文件（默认）
- 生产环境：使用项目根目录的 `.env.production` 文件
- 所有环境相关的操作都在项目根目录执行

> **网络连接提示**:
> - 如果数据库在同一服务器: 使用服务器的内网 IP（如 `192.168.1.100`）或 `host.docker.internal`（Mac/Windows）
> - 如果数据库在其他服务器: 使用数据库服务器的 IP 或域名
> - **不要使用** `localhost` 或 `127.0.0.1`（容器内无法访问宿主机）
> - 确保数据库防火墙允许来自 Docker 容器的连接

### 4. 生成 RSA 密钥

```bash
# 创建密钥目录
mkdir -p keys

# 方式 1: 使用 Python 脚本（推荐）
cd backend
python3 scripts/generate_keys.py
cd ..

# 方式 2: 使用 OpenSSL
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
```

> **重要**: 请妥善保管 `keys/` 目录，丢失后所有 Token 将失效！

### 5. 启动服务

#### 方式 A: 使用快速部署脚本（推荐）

```bash
# 运行一键部署脚本
./scripts/setup-production.sh
```

脚本会自动完成：
- 检查 Docker 环境
- 创建 .env 配置文件模板
- 生成 RSA 密钥
- 验证配置
- 构建并启动服务
- 健康检查

#### 方式 B: 手动启动

```bash
# 构建镜像
docker-compose -f docker-compose-production.yml build

# 启动服务
docker-compose -f docker-compose-production.yml up -d

# 查看服务状态
docker-compose -f docker-compose-production.yml ps

# 查看日志
docker-compose -f docker-compose-production.yml logs -f
```

### 6. 验证部署

```bash
# 检查服务健康状态
curl http://localhost:8080/health

# 应该返回类似:
# {"status":"healthy","timestamp":"..."}

# 查看 API 文档
# 浏览器访问: http://localhost:8080/docs
```

**如果健康检查失败**，查看日志排查问题：

```bash
# 查看容器日志
docker-compose -f docker-compose-production.yml logs backend

# 常见问题:
# - 数据库连接失败: 检查 DATABASE_URL 是否正确
# - Redis 连接失败: 检查 REDIS_URL 是否正确
# - 密钥文件不存在: 确保 keys/ 目录已挂载
```

### 7. 配置反向代理（Nginx）

创建 Nginx 配置文件 `/etc/nginx/sites-available/authhub`:

```nginx
upstream authhub_backend {
    server localhost:8080;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    # 强制 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/your-domain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/your-domain.com.key;
    
    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志配置
    access_log /var/log/nginx/authhub-access.log;
    error_log /var/log/nginx/authhub-error.log;

    # 客户端上传限制
    client_max_body_size 10M;

    # 反向代理配置
    location / {
        proxy_pass http://authhub_backend;
        proxy_http_version 1.1;
        
        # 请求头配置
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket 支持（如果需要）
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # 健康检查端点（不需要缓存）
    location /health {
        proxy_pass http://authhub_backend/health;
        access_log off;
    }

    # 静态资源缓存（如果前端也部署在这里）
    location /static {
        proxy_pass http://authhub_backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/authhub /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 8. 数据库连接故障排查

如果遇到数据库连接问题，可以使用以下方法排查：

```bash
# 1. 从容器内测试数据库连接
docker exec -it authhub-backend bash
apt-get update && apt-get install -y postgresql-client
psql "postgresql://authhub:password@your-db-host:5432/authhub"

# 2. 检查网络连通性
docker exec -it authhub-backend ping your-db-host

# 3. 检查 DNS 解析
docker exec -it authhub-backend nslookup your-db-host

# 4. 使用 host.docker.internal（仅 Mac/Windows）
# 如果数据库在宿主机，可以在 .env 中使用:
DATABASE_URL=postgresql://authhub:password@host.docker.internal:5432/authhub

# 5. Linux 宿主机网络访问
# Linux 需要使用网桥 IP，通常是 172.17.0.1
DATABASE_URL=postgresql://authhub:password@172.17.0.1:5432/authhub
# 或者使用 --network host 模式（不推荐）
```

### 9. 设置开机自启

```bash
# Docker 服务开机自启
sudo systemctl enable docker

# 创建 systemd 服务（可选）
sudo tee /etc/systemd/system/authhub.service > /dev/null <<EOF
[Unit]
Description=AuthHub Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/AuthHub
ExecStart=/usr/bin/docker-compose -f docker-compose-production.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose-production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable authhub.service
sudo systemctl start authhub.service
```

## 方式二：源码部署

### 1. 安装系统依赖

#### Ubuntu/Debian

```bash
# 更新包管理器
sudo apt update

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安装 Redis
sudo apt install -y redis-server

# 安装其他工具
sudo apt install -y git curl build-essential
```

#### CentOS/RHEL

```bash
# 安装 Python 3.11
sudo yum install -y python3.11 python3.11-devel

# 安装 Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安装 PostgreSQL
sudo yum install -y postgresql15-server postgresql15-contrib

# 安装 Redis
sudo yum install -y redis

# 初始化 PostgreSQL
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2. 配置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 PostgreSQL 中执行以下命令:
CREATE DATABASE authhub;
CREATE USER authhub WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE authhub TO authhub;
\q
```

配置 Redis（编辑 `/etc/redis/redis.conf`）:

```conf
# 设置密码
requirepass your_redis_password

# 启用持久化
appendonly yes
```

重启 Redis:

```bash
sudo systemctl restart redis
```

### 3. 安装项目依赖

```bash
# 克隆项目
git clone https://github.com/your-org/AuthHub.git
cd AuthHub

# 安装 UV (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 安装 pnpm
npm install -g pnpm

# 后端依赖
cd backend
uv sync
cd ..

# 前端依赖
cd frontend
pnpm install
cd ..
```

### 4. 配置环境变量

创建 `.env` 文件（在项目根目录）：

```bash
# 应用配置
APP_NAME=AuthHub
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=postgresql+asyncpg://authhub:your_password@localhost:5432/authhub

# Redis配置
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# JWT配置
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_PRIVATE_KEY_PATH=./keys/private_key.pem
JWT_PUBLIC_KEY_PATH=./keys/public_key.pem

# 飞书配置
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret

# CORS配置
CORS_ORIGINS=["https://your-domain.com"]

# 日志配置
LOG_LEVEL=INFO
```

**配置说明**：
- 所有环境相关的操作都在项目根目录执行
- 后端服务会自动加载项目根目录的 `.env` 文件
- 数据库迁移也会使用相同的配置文件，确保环境一致性


### 5. 初始化数据库和密钥

```bash
cd backend

# 生成 RSA 密钥对
python scripts/generate_keys.py

# 运行数据库迁移
uv run alembic upgrade head

cd ..
```

### 6. 构建前端

```bash
cd frontend

# 设置后端 API 地址
echo "VITE_API_URL=https://your-domain.com" > .env

# 构建生产版本
pnpm build

cd ..
```

### 7. 配置 Systemd 服务

创建后端服务 `/etc/systemd/system/authhub-backend.service`:

```ini
[Unit]
Description=AuthHub Backend Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/AuthHub/backend
Environment="PATH=/path/to/AuthHub/backend/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/path/to/AuthHub/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/authhub/backend.log
StandardError=append:/var/log/authhub/backend-error.log

[Install]
WantedBy=multi-user.target
```

创建日志目录:

```bash
sudo mkdir -p /var/log/authhub
sudo chown www-data:www-data /var/log/authhub
```

启动服务:

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start authhub-backend

# 开机自启
sudo systemctl enable authhub-backend

# 查看状态
sudo systemctl status authhub-backend

# 查看日志
sudo journalctl -u authhub-backend -f
```

### 8. 配置 Nginx 提供前端静态文件

修改 Nginx 配置，添加前端静态文件服务:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 配置 (同上)
    # ...

    # 前端静态文件
    root /path/to/AuthHub/frontend/dist;
    index index.html;

    # 前端路由处理（SPA）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://localhost:8000;
        # proxy 配置 (同上)
        # ...
    }

    # API 文档
    location /docs {
        proxy_pass http://localhost:8000/docs;
        # proxy 配置 (同上)
        # ...
    }
}
```

## 配置说明

### 核心环境变量说明

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接字符串 | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | ✅ | Redis 连接字符串 | `redis://:password@host:6379/0` |
| `FEISHU_APP_ID` | ✅ | 飞书应用 ID | `cli_xxxxxxxx` |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 Secret | `xxxxxxxxxxxx` |
| `JWT_PRIVATE_KEY_PATH` | ✅ | JWT 私钥路径 | `./keys/private_key.pem` |
| `JWT_PUBLIC_KEY_PATH` | ✅ | JWT 公钥路径 | `./keys/public_key.pem` |
| `CORS_ORIGINS` | ✅ | 允许的跨域来源 | `["https://app.com"]` |
| `DEBUG` | ❌ | 调试模式 | `false` |
| `LOG_LEVEL` | ❌ | 日志级别 | `INFO` |

### 飞书应用配置

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 配置应用权限：
   - `contact:user.base:readonly` - 获取用户基本信息
   - `contact:user.employee_id:readonly` - 获取用户雇员 ID
4. 配置 OAuth 回调地址：
   ```
   https://your-domain.com/api/auth/feishu/callback
   ```
5. 获取 `App ID` 和 `App Secret`

## 监控和维护

### 日志查看

Docker 部署:

```bash
# 查看所有服务日志
docker-compose -f docker-compose-production.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose-production.yml logs -f backend
docker-compose -f docker-compose-production.yml logs -f postgres
docker-compose -f docker-compose-production.yml logs -f redis
```

源码部署:

```bash
# 后端日志
sudo journalctl -u authhub-backend -f

# Nginx 日志
sudo tail -f /var/log/nginx/authhub-access.log
sudo tail -f /var/log/nginx/authhub-error.log
```

### 数据备份

#### PostgreSQL 备份

```bash
# Docker 环境
docker exec authhub-postgres pg_dump -U authhub authhub > backup_$(date +%Y%m%d_%H%M%S).sql

# 源码环境
pg_dump -U authhub -h localhost authhub > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Redis 备份

```bash
# Docker 环境
docker exec authhub-redis redis-cli --raw -a your_redis_password save
docker cp authhub-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d_%H%M%S).rdb

# 源码环境
redis-cli -a your_redis_password save
cp /var/lib/redis/dump.rdb ./redis_backup_$(date +%Y%m%d_%H%M%S).rdb
```

#### 密钥备份

```bash
# 备份 RSA 密钥（非常重要！）
tar -czf keys_backup_$(date +%Y%m%d_%H%M%S).tar.gz keys/
```

### 自动备份脚本

创建 `/usr/local/bin/authhub-backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backup/authhub"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec authhub-postgres pg_dump -U authhub authhub | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份 Redis
docker exec authhub-redis redis-cli --raw -a your_redis_password save
docker cp authhub-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# 备份密钥
tar -czf $BACKUP_DIR/keys_$DATE.tar.gz -C /path/to/AuthHub keys/

# 删除 7 天前的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

添加到 crontab（每天凌晨 2 点备份）:

```bash
chmod +x /usr/local/bin/authhub-backup.sh
crontab -e
# 添加以下行
0 2 * * * /usr/local/bin/authhub-backup.sh >> /var/log/authhub-backup.log 2>&1
```

## 常见问题

### 1. 数据库连接失败

**问题**: `sqlalchemy.exc.OperationalError: could not connect to server`

**解决方案**:

```bash
# 检查 PostgreSQL 是否运行
docker-compose ps postgres  # Docker 环境
sudo systemctl status postgresql  # 源码环境

# 检查连接字符串
echo $DATABASE_URL

# 测试连接
psql "postgresql://authhub:password@localhost:5432/authhub"
```

### 2. Redis 连接失败

**问题**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**解决方案**:

```bash
# 检查 Redis 是否运行
docker-compose ps redis  # Docker 环境
sudo systemctl status redis  # 源码环境

# 测试连接
redis-cli -a your_password ping
```

### 3. 密钥文件不存在

**问题**: `FileNotFoundError: [Errno 2] No such file or directory: './keys/private_key.pem'`

**解决方案**:

```bash
cd backend
python scripts/generate_keys.py
```

### 4. 飞书回调失败

**问题**: 飞书登录后回调 404

**解决方案**:

1. 检查飞书后台回调地址配置
2. 确保地址格式正确: `https://your-domain.com/api/auth/feishu/callback`
3. 检查 Nginx 反向代理配置
4. 查看后端日志排查问题

### 5. CORS 错误

**问题**: `Access to fetch at 'xxx' from origin 'xxx' has been blocked by CORS policy`

**解决方案**:

在 `.env` 中添加前端域名到 `CORS_ORIGINS`:

```bash
CORS_ORIGINS=["https://your-frontend-domain.com", "http://localhost:3000"]
```

### 6. 内存不足

**问题**: 容器频繁重启，日志显示内存不足

**解决方案**:

在 `docker-compose-production.yml` 中限制内存:

```yaml
services:
  backend:
    # ...
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### 7. 端口被占用

**问题**: `Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use`

**解决方案**:

```bash
# 查找占用端口的进程
sudo lsof -i :8080
sudo netstat -tlnp | grep 8080

# 修改端口映射
# 在 docker-compose-production.yml 中修改:
ports:
  - "8081:8080"  # 改用 8081 端口
```

## 安全建议

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# 数据库和 Redis 不对外开放
```

### 2. 定期更新

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新 Docker 镜像
docker-compose -f docker-compose-production.yml pull
docker-compose -f docker-compose-production.yml up -d
```

### 3. 使用强密码

- PostgreSQL 密码至少 16 位
- Redis 密码至少 32 位
- 使用随机生成器生成密码

### 4. SSL 证书

#### 方式 A: Cloudflare（推荐，最简单）

使用 Cloudflare 提供的**免费 SSL 证书**：

1. 注册 [Cloudflare](https://www.cloudflare.com/) 账号（免费）
2. 添加你的域名到 Cloudflare
3. 配置 DNS A 记录指向你的服务器 IP，开启"代理状态"（橙色云朵）
4. **SSL/TLS** → **概述** → 选择 **灵活** 或 **完全（严格）** 模式

✅ **零配置即可使用 HTTPS**，Cloudflare 自动处理 SSL！

详细教程: [SSL 证书配置指南](./ssl-certificate-guide.md)

#### 方式 B: Let's Encrypt（免费证书）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

详细教程: [SSL 证书配置指南](./ssl-certificate-guide.md)

### 5. 备份密钥

RSA 密钥是 JWT Token 签发和验证的核心，丢失后所有 Token 将失效！

```bash
# 将密钥备份到安全位置
scp -r keys/ backup-server:/secure-backup/authhub/
```

## 性能优化

### 1. PostgreSQL 调优

编辑 PostgreSQL 配置（`postgresql.conf`）:

```conf
# 根据服务器内存调整
shared_buffers = 256MB              # 25% 内存
effective_cache_size = 1GB          # 75% 内存
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
max_connections = 100
```

### 2. Redis 调优

编辑 Redis 配置（`redis.conf`）:

```conf
# 内存限制
maxmemory 512mb
maxmemory-policy allkeys-lru

# 持久化优化
save 900 1
save 300 10
save 60 10000

# 关闭 RDB 压缩（如果 CPU 紧张）
rdbcompression no
```

### 3. Nginx 调优

```nginx
# 工作进程数（通常等于 CPU 核心数）
worker_processes auto;

# 每个进程的最大连接数
events {
    worker_connections 2048;
    use epoll;
}

http {
    # 开启 gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript;
    
    # 连接超时
    keepalive_timeout 65;
    
    # 缓冲区大小
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    client_max_body_size 8m;
    large_client_header_buffers 2 1k;
}
```

## 扩展阅读

- [AuthHub 架构设计](../architecture/overview.md)
- [飞书 SSO 集成指南](../sso-integration-guide.md)
- [Python SDK 使用指南](../../sdk/python/README.md)
- [TypeScript SDK 使用指南](../../sdk/typescript/README.md)
- [API 文档](http://localhost:8080/docs)

## 获取帮助

如果遇到问题：

1. 查看日志定位问题
2. 搜索 [GitHub Issues](https://github.com/your-org/AuthHub/issues)
3. 提交新的 Issue
4. 联系技术支持

---

**祝部署顺利！** 🚀

