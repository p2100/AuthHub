# AuthHub 后端服务

基于飞书的统一SSO认证和权限配置平台后端服务。

## 功能特性

- 🔐 飞书OAuth2.0单点登录
- 🎫 JWT Token管理(RS256签名)
- 👥 多命名空间权限模型
- 🔑 RBAC权限管理
- 🌐 系统注册和配置同步
- 📊 审计日志
- 🚀 高性能本地权限校验

## 技术栈

- FastAPI 0.104+
- SQLAlchemy 2.0
- PostgreSQL 15+
- Redis 7+
- PyJWT (RS256)
- Alembic

## 快速开始

### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
cd ..
cp .env.example .env
# 编辑.env文件,填写数据库和Redis连接信息
```

**重要**：环境变量文件统一放在项目根目录，无论是使用Docker还是本地运行，都会自动加载根目录的 `.env` 文件。

### 2. 安装UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 生成RSA密钥对

```bash
python scripts/generate_keys.py
```

### 5. 初始化数据库

```bash
alembic upgrade head
```

### 6. 运行服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── core/          # 核心模块
│   ├── auth/          # 认证模块
│   ├── systems/       # 系统管理
│   ├── rbac/          # RBAC权限
│   ├── users/         # 用户管理
│   ├── audit/         # 审计日志
│   ├── schemas/       # Pydantic模式
│   └── main.py        # 应用入口
├── alembic/           # 数据库迁移
├── scripts/           # 工具脚本
└── tests/             # 测试
```

## 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black app/
ruff check app/
```

### 类型检查

```bash
mypy app/
```

## 环境配置说明

### 环境变量管理

本项目采用统一的配置文件管理策略：

- **开发环境**：使用项目根目录的 `.env` 文件
- **生产环境**：使用项目根目录的 `.env.production` 文件
- **数据库迁移**：同样使用根目录的配置文件，确保环境一致性

### 配置文件示例

项目根目录的环境变量示例 (`.env.example`)：

```bash
# 应用配置
DEBUG=true
PORT=8080

# 数据库配置
DATABASE_URL=postgresql+asyncpg://testuser:testpass123@localhost:5432/testdb

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 飞书配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# CORS配置（本地开发）
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 启动方式

**方式一：Docker 启动（推荐）**

```bash
# 确保已在项目根目录配置好 .env 文件
cd /path/to/AuthHub

# 启动后端服务
docker compose up backend

# 启动完整服务（前端+后端）
docker compose up
```

**方式二：本地开发服务器**

```bash
# 确保已在项目根目录配置好 .env 文件
cd /path/to/AuthHub/backend

# 启动开发服务器（带热重载）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 环境变量加载机制

后端使用 `pydantic-settings` 管理配置，会自动从项目根目录的 `.env` 文件加载：

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... 配置字段 ...

    model_config = SettingsConfigDict(
        env_file="../.env",  # 从项目根目录加载
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
```

**优势**：
- 所有环境使用统一的配置文件位置
- 避免在不同目录运行命令导致的配置混乱
- 数据库迁移和应用使用相同的配置
- 简化开发和部署流程

