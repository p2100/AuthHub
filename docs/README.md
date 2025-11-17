# AuthHub 文档中心

欢迎使用 AuthHub！这里是完整的文档索引，帮助你快速找到所需信息。

## 🚀 快速开始

### 新用户推荐路径

1. **了解架构** → [系统架构概述](./architecture/overview.md)
2. **选择方案** → [SDK 完全接入指南](./sdk/complete-integration-guide.md)
3. **开始集成** → [SSO 登录集成](./sso-integration-guide.md)
4. **查看示例** → [示例代码](#示例代码)

---

## 📚 核心文档

### SDK 集成指南

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| [SDK 完全接入指南](./sdk/complete-integration-guide.md) | ⭐ 推荐首选 | 前后端分离架构的完整接入步骤 |
| [SSO 登录集成指南](./sso-integration-guide.md) | 详细的 SSO 集成说明 | FastAPI/React/Vue 集成 |
| [Python SDK 文档](../sdk/python/README.md) | Python SDK API 文档 | 后端集成 |
| [TypeScript SDK 文档](../sdk/typescript/README.md) | TypeScript SDK API 文档 | 前端集成 |

### 认证与授权

| 文档 | 说明 |
|------|------|
| [认证实现说明](./authentication-implementation.md) | 认证系统的技术实现 |
| [资源绑定指南](./rbac/resource-binding-guide.md) | RBAC 权限模型的资源绑定 |

### 架构与设计

| 文档 | 说明 |
|------|------|
| [系统架构概述](./architecture/overview.md) | AuthHub 整体架构设计 |

---

## 🔧 故障排查

### SDK 相关问题

| 文档 | 解决的问题 |
|------|-----------|
| [React SSO 修复清单](./sdk/react-sso-fix-checklist.md) | 登录重定向、CORS、Cookie 等常见问题 |
| [React SSO 重定向修复](./sdk/react-sso-redirect-fix.md) | 登录后跳转到后端页面的问题 |
| [TypeScript 构建修复](./sdk/typescript-build-fixes.md) | TypeScript SDK 构建问题 |
| [包名变更说明](./sdk/package-name-change.md) | SDK 包名更新历史 |

---

## 💻 示例代码

### Python 示例

```bash
# 后端示例位置
sdk/python/examples/
├── fastapi_sso_example.py    # FastAPI SSO 完整示例
├── fastapi_example.py         # FastAPI 基础集成
└── flask_example.py           # Flask 集成示例
```

### TypeScript 示例

```bash
# 前端示例位置
sdk/typescript/examples/
├── react-sso/                 # React SSO 完整示例（推荐）
│   ├── src/
│   │   ├── lib/auth-client.ts
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Callback.tsx
│   │   │   └── Dashboard.tsx
│   │   └── App.tsx
│   └── README.md
└── [其他示例...]
```

---

## 🎯 按使用场景查找

### 场景 1: 我要集成 SSO 登录

**推荐路径**:
1. 阅读 [SDK 完全接入指南](./sdk/complete-integration-guide.md)
2. 参考 [FastAPI SSO 示例](../sdk/python/examples/fastapi_sso_example.py)
3. 参考 [React SSO 示例](../sdk/typescript/examples/react-sso/)

**涉及技术**:
- 后端: Python FastAPI + AuthHub SDK
- 前端: React + TypeScript
- 认证: 飞书 OAuth

### 场景 2: 遇到登录问题

**常见问题**:
- ❌ 登录后跳转到后端页面
- ❌ /api/me 返回 401
- ❌ CORS 错误
- ❌ Cookie 未设置

**解决方案**: [React SSO 修复清单](./sdk/react-sso-fix-checklist.md)

### 场景 3: 实现权限控制

**推荐文档**:
1. [资源绑定指南](./rbac/resource-binding-guide.md) - RBAC 权限模型
2. [认证实现说明](./authentication-implementation.md) - 权限验证流程

**代码示例**:
```python
# 检查权限
if not authhub_client.check_permission(user, "document", "write"):
    raise HTTPException(status_code=403, detail="权限不足")
```

### 场景 4: 构建失败

**TypeScript 构建问题**: [TypeScript 构建修复](./sdk/typescript-build-fixes.md)

**Python 依赖问题**: 检查 `requirements.txt` 和 Python 版本

---

## 🛠️ 开发与测试

### 测试文档

| 文档 | 说明 |
|------|------|
| [数据库测试指南](./TESTING_DATABASES.md) | 数据库相关的测试说明 |

### 环境要求

**后端**:
- Python 3.8+
- FastAPI / Flask
- Redis (用于缓存)
- PostgreSQL / MySQL (数据库)

**前端**:
- Node.js 16+
- React 18+ / Vue 3+
- TypeScript 4.5+

---

## 📖 文档贡献

### 文档结构

```
docs/
├── README.md                    # 本文档（索引）
├── architecture/                # 架构设计
│   └── overview.md
├── sdk/                         # SDK 相关
│   ├── complete-integration-guide.md
│   ├── react-sso-fix-checklist.md
│   ├── react-sso-redirect-fix.md
│   ├── typescript-build-fixes.md
│   └── package-name-change.md
├── rbac/                        # 权限控制
│   └── resource-binding-guide.md
├── sso-integration-guide.md     # SSO 集成
├── authentication-implementation.md
└── TESTING_DATABASES.md
```

### 文档规范

1. **文档命名**: 使用 kebab-case（小写-连字符）
2. **文档位置**: 
   - SDK 相关 → `docs/sdk/`
   - 架构设计 → `docs/architecture/`
   - 权限相关 → `docs/rbac/`
3. **格式要求**: Markdown 格式，包含代码示例和流程图
4. **更新日期**: 文档底部标注最后更新日期

### 贡献指南

欢迎贡献文档！请遵循以下步骤：

1. Fork 本仓库
2. 创建文档或更新现有文档
3. 确保文档格式正确，代码可运行
4. 提交 Pull Request

---

## 🔗 快速链接

### 外部资源

- [飞书开放平台](https://open.feishu.cn/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)

### 内部链接

- [GitHub 仓库](https://github.com/your-org/authhub)
- [Issue 追踪](https://github.com/your-org/authhub/issues)
- [更新日志](../CHANGELOG.md)

---

## ❓ 获取帮助

### 在开始之前

1. ✅ 检查[常见问题](#故障排查)
2. ✅ 查看[示例代码](#示例代码)
3. ✅ 阅读相关文档

### 仍然有问题？

1. **搜索 Issues**: 查看是否有类似问题
2. **创建 Issue**: 描述问题、环境、复现步骤
3. **联系团队**: [support@authhub.com](mailto:support@authhub.com)

---

## 📝 文档更新记录

| 日期 | 更新内容 |
|------|---------|
| 2025-11-17 | 创建文档索引，新增 SDK 完全接入指南和修复文档 |
| 2025-11-17 | 修复 React SSO 登录重定向问题，更新相关文档 |

---

**最后更新**: 2025-11-17  
**维护团队**: AuthHub Team

