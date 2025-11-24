# AuthHub 生产环境快速部署

> 适用于有外部 PostgreSQL 和 Redis 的场景

## 🎯 5 分钟快速部署

### 前置要求

✅ Docker 20.10+  
✅ Docker Compose 2.0+  
✅ 外部 PostgreSQL 15+  
✅ 外部 Redis 7+  
✅ 飞书企业自建应用

### 部署架构

```mermaid
%%{init: {'theme':'dark'}}%%
graph TB
    subgraph Internet["🌐 互联网"]
        User[用户浏览器]
        Feishu[飞书开放平台]
    end
    
    subgraph Server["🖥️ 自建服务器"]
        Nginx[Nginx<br/>反向代理]
        
        subgraph Docker["🐳 Docker 环境"]
            AuthHub[AuthHub 容器<br/>Backend + Frontend]
        end
        
        subgraph External["💾 外部数据库"]
            Postgres[(PostgreSQL 15+)]
            Redis[(Redis 7+)]
        end
    end
    
    User -->|HTTPS| Nginx
    Feishu -->|OAuth回调| Nginx
    Nginx -->|proxy_pass| AuthHub
    AuthHub -->|SQL| Postgres
    AuthHub -->|Cache/PubSub| Redis
    
    style AuthHub fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Postgres fill:#336791,stroke:#1A3A5A,color:#fff
    style Redis fill:#DC382D,stroke:#8B1F1A,color:#fff
    style Nginx fill:#009639,stroke:#005A22,color:#fff
```

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-org/AuthHub.git
cd AuthHub

# 2. 运行部署脚本
./scripts/setup-production.sh
```

脚本会自动：
- ✅ 检查 Docker 环境
- ✅ 生成 .env 配置模板
- ✅ 生成 RSA 密钥对
- ✅ 验证配置完整性
- ✅ 构建并启动服务
- ✅ 健康检查

### 手动部署步骤

#### 1️⃣ 准备数据库

```sql
-- PostgreSQL
CREATE DATABASE authhub;
CREATE USER authhub WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE authhub TO authhub;
```

```bash
# Redis (编辑 redis.conf)
requirepass your_redis_password
```

#### 2️⃣ 配置环境变量

创建 `.env` 文件：

```bash
# 应用配置
PORT=8080

# 外部数据库（⚠️ 不能使用 localhost）
DATABASE_URL=postgresql://authhub:password@192.168.1.100:5432/authhub
REDIS_URL=redis://:password@192.168.1.100:6379/0

# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxx

# CORS（改为你的域名）
CORS_ORIGINS=["https://your-domain.com"]

# JWT 密钥路径（Docker 内部路径）
JWT_PRIVATE_KEY_PATH=/app/keys/private_key.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public_key.pem
```

> 💡 **网络连接提示**:
> - 同一服务器: 使用内网 IP（如 `192.168.1.100`）
> - Linux 宿主机: 可用 `172.17.0.1`（Docker 默认网桥）
> - Mac/Windows 宿主机: 可用 `host.docker.internal`

#### 3️⃣ 生成密钥

```bash
mkdir -p keys
cd backend && python3 scripts/generate_keys.py && cd ..
```

#### 4️⃣ 启动服务

```bash
# 构建并启动
docker-compose -f docker-compose-production.yml up -d

# 查看日志
docker-compose -f docker-compose-production.yml logs -f

# 检查健康状态
curl http://localhost:8080/health
```

#### 5️⃣ 配置 Nginx 和 SSL

##### 选项 A: 使用 Cloudflare（推荐，最简单）

1. 添加域名到 [Cloudflare](https://www.cloudflare.com/)（免费）
2. 配置 DNS，开启代理（橙色云朵）
3. 选择 SSL 模式：**灵活** 或 **完全（严格）**

Nginx 配置（灵活模式，无需证书）:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 获取真实 IP
    real_ip_header CF-Connecting-IP;
    set_real_ip_from 0.0.0.0/0;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

✅ **完成！** 访问 `https://your-domain.com` 即可，Cloudflare 自动提供 SSL！

##### 选项 B: 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 自动配置
sudo certbot --nginx -d your-domain.com
```

📖 **详细 SSL 配置**: [SSL 证书配置指南](./ssl-certificate-guide.md)

#### 6️⃣ 配置飞书回调

飞书开放平台 → 你的应用 → 安全设置 → 重定向 URL:

```
https://your-domain.com/api/auth/feishu/callback
```

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose-production.yml ps

# 查看日志
docker-compose -f docker-compose-production.yml logs -f

# 重启服务
docker-compose -f docker-compose-production.yml restart

# 停止服务
docker-compose -f docker-compose-production.yml down

# 更新服务
git pull
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up -d
```

## 🐛 故障排查

### 数据库连接失败

```bash
# 测试连接
docker exec -it authhub-backend bash
apt-get update && apt-get install -y postgresql-client
psql "postgresql://authhub:password@your-db-host:5432/authhub"

# 检查网络
docker exec -it authhub-backend ping your-db-host
```

**常见原因**:
- ❌ 使用了 `localhost` → 改用实际 IP
- ❌ 防火墙阻止 → 开放端口
- ❌ 数据库未监听外网 → 修改 `listen_addresses = '*'`

### Redis 连接失败

```bash
# 测试连接
docker exec -it authhub-backend bash
apt-get update && apt-get install -y redis-tools
redis-cli -h your-redis-host -p 6379 -a password ping
```

### 查看完整日志

```bash
# 容器日志
docker logs authhub-backend --tail 100 -f

# 应用日志（如果配置了文件日志）
docker exec -it authhub-backend tail -f /var/log/authhub/app.log
```

## 📊 监控检查

```bash
# 健康检查
curl http://localhost:8080/health

# API 文档
open http://localhost:8080/docs

# 容器资源使用
docker stats authhub-backend
```

## 🔐 安全建议

1. **使用强密码**: 数据库密码至少 16 位
2. **配置防火墙**: 只开放 80/443/22 端口
3. **启用 SSL**: 使用 Let's Encrypt 免费证书
4. **备份密钥**: `keys/` 目录非常重要！
5. **定期更新**: 及时更新系统和 Docker 镜像

## 📦 备份

```bash
# 备份数据库
docker exec authhub-postgres pg_dump -U authhub authhub > backup.sql

# 备份密钥（非常重要！）
tar -czf keys-backup.tar.gz keys/

# 备份配置
cp .env .env.backup
```

## 🚀 性能优化

### PostgreSQL 连接池

默认配置适用于小型部署，如需优化：

```python
# backend/app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 连接池大小
    max_overflow=10,        # 最大溢出连接
    pool_pre_ping=True,     # 连接前 ping
)
```

### Redis 连接

```python
# backend/app/core/cache.py
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,     # 最大连接数
)
```

## 📖 相关文档

- [完整部署指南](./self-hosted-deployment.md)
- [架构设计](../architecture/overview.md)
- [API 文档](http://localhost:8080/docs)
- [故障排查](./troubleshooting.md)

## 🆘 获取帮助

- GitHub Issues: https://github.com/your-org/AuthHub/issues
- 文档: https://your-domain.com/docs
- Email: support@your-company.com

---

**部署完成后别忘了** ⭐️ Star 我们的项目！

