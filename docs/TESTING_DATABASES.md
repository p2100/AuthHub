# 本地测试数据库部署指南

本文档介绍如何在本地快速启动测试用的 PostgreSQL 和 Redis 实例。

## 方法 1: 使用 Docker Compose (推荐)

### 前提条件

- 安装 [Docker](https://docker.com/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 启动步骤

1. 在项目根目录创建 `docker-compose.test.yml` 文件：

```yaml
version: '3.8'

services:
  postgres-test:
    image: postgres:15-alpine
    container_name: postgres-test
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass123
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
    volumes:
      - postgres-test-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis-test:
    image: redis:7-alpine
    container_name: redis-test
    ports:
      - "6379:6379"
    volumes:
      - redis-test-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres-test-data:
  redis-test-data:
```

2. 启动测试数据库：

```bash
docker-compose -f docker-compose.test.yml up -d
```

3. 查看运行状态：

```bash
docker-compose -f docker-compose.test.yml ps
```

4. 查看日志：

```bash
docker-compose -f docker-compose.test.yml logs -f
```

5. 停止测试数据库：

```bash
docker-compose -f docker-compose.test.yml down
```

### 连接信息

**PostgreSQL:**
- Host: localhost
- Port: 5432
- Database: testdb
- Username: testuser
- Password: testpass123
- 连接字符串: `postgresql://testuser:testpass123@localhost:5432/testdb`

**Redis:**
- Host: localhost
- Port: 6379
- 连接字符串: `redis://localhost:6379`

### 持久化数据

测试数据默认被 Docker volume 持久化。如果需要清除所有测试数据：

```bash
docker-compose -f docker-compose.test.yml down -v
```

## 方法 2: 本地安装

### PostgreSQL

#### macOS (使用 Homebrew)

```bash
# 安装 PostgreSQL
brew install postgresql@15

# 启动 PostgreSQL 服务
brew services start postgresql@15

# 连接 PostgreSQL
psql postgres

# 创建测试数据库和用户 (在 psql 中执行)
CREATE DATABASE testdb;
CREATE USER testuser WITH PASSWORD 'testpass123';
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
\q
```

#### Ubuntu/Debian

```bash
# 安装 PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动并启用服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到 postgres 用户
sudo -i -u postgres

# 创建测试数据库和用户
psql
CREATE DATABASE testdb;
CREATE USER testuser WITH PASSWORD 'testpass123';
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
\q
exit
```

### Redis

#### macOS (使用 Homebrew)

```bash
# 安装 Redis
brew install redis

# 启动 Redis 服务
brew services start redis

# 测试连接
redis-cli ping
```

#### Ubuntu/Debian

```bash
# 安装 Redis
sudo apt update
sudo apt install redis-server

# 启动并启用服务
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 测试连接
redis-cli ping
```

## 验证连接

### PostgreSQL

使用 psql 验证：
```bash
psql -h localhost -U testuser -d testdb -W
```

使用 Python 验证：
```python
import psycopg2

conn = psycopg2.connect(
    dbname="testdb",
    user="testuser",
    password="testpass123",
    host="localhost",
    port=5432
)
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
```

### Redis

使用 redis-cli 验证：
```bash
redis-cli ping
```

使用 Python 验证：
```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('test', 'Hello Redis!')
print(r.get('test'))
```

## 常见问题

### Docker 容器无法连接

**问题**: 端口被占用
**解决方案**: 修改 `docker-compose.test.yml` 中的端口映射

```yaml
ports:
  - "5433:5432"  # PostgreSQL 使用 5433
  - "6380:6379"  # Redis 使用 6380
```

### 数据库存储空间不足

**问题**: 测试数据占用了大量磁盘空间
**解决方案**: 清理 Docker 卷

```bash
# 删除所有未使用的卷
docker volume prune

# 仅删除测试数据库的卷
docker volume rm $(docker volume ls -q | grep -E 'postgres-test|redis-test')
```

## 注意事项

1. **测试环境**: 此配置仅适用于本地测试，不应用于生产环境
2. **默认端口**: 默认使用 PostgreSQL 5432 和 Redis 6379 端口
3. **安全凭证**: 使用简单密码，仅适合本地开发测试
4. **数据清理**: 建议定期清理测试数据以节省磁盘空间
