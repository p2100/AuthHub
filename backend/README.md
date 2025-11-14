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

### 1. 安装UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件,填写配置
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

