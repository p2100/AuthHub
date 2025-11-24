# AuthHub 部署工作流程

本文档展示 AuthHub 各种部署方式的完整工作流程。

## 🎯 生产环境部署流程（使用外部数据库）

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart TD
    Start([开始部署]) --> CheckEnv{检查环境}
    
    CheckEnv -->|缺少| InstallDocker[安装 Docker<br/>Docker Compose]
    CheckEnv -->|完整| PrepareDB[准备外部数据库]
    InstallDocker --> PrepareDB
    
    PrepareDB --> CreatePG[创建 PostgreSQL<br/>数据库和用户]
    CreatePG --> ConfigRedis[配置 Redis<br/>密码认证]
    
    ConfigRedis --> CloneRepo[克隆项目<br/>git clone]
    CloneRepo --> CreateEnv[创建 .env 文件<br/>配置数据库连接]
    
    CreateEnv --> GenKeys[生成 RSA 密钥<br/>python generate_keys.py]
    GenKeys --> ConfigFeishu[配置飞书应用<br/>App ID & Secret]
    
    ConfigFeishu --> Validate{验证配置}
    Validate -->|有错误| FixConfig[修复配置错误]
    FixConfig --> Validate
    
    Validate -->|正确| Build[构建 Docker 镜像<br/>docker-compose build]
    Build --> Deploy[启动服务<br/>docker-compose up -d]
    
    Deploy --> Wait[等待服务启动<br/>健康检查]
    Wait --> Health{健康检查}
    
    Health -->|失败| CheckLogs[查看日志排查]
    CheckLogs --> FixIssue[修复问题]
    FixIssue --> Deploy
    
    Health -->|成功| ConfigNginx[配置 Nginx<br/>反向代理]
    ConfigNginx --> ConfigSSL[配置 SSL 证书<br/>Let's Encrypt]
    
    ConfigSSL --> ConfigFeishuCallback[配置飞书回调<br/>OAuth URL]
    ConfigFeishuCallback --> TestSSO[测试 SSO 登录]
    
    TestSSO --> Success{测试成功?}
    Success -->|失败| Debug[调试问题]
    Debug --> TestSSO
    
    Success -->|成功| Backup[设置自动备份]
    Backup --> Monitor[配置监控告警]
    Monitor --> Done([部署完成✅])
    
    style Start fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Done fill:#34A853,stroke:#1F6E34,color:#fff
    style Health fill:#FBBC04,stroke:#B87E00,color:#fff
    style Success fill:#FBBC04,stroke:#B87E00,color:#fff
    style CheckLogs fill:#EA4335,stroke:#A52E24,color:#fff
    style Debug fill:#EA4335,stroke:#A52E24,color:#fff
```

## 🔄 网络连接关系

```mermaid
%%{init: {'theme':'dark'}}%%
graph LR
    subgraph Internet["🌐 互联网"]
        User[👤 用户]
        Feishu[飞书平台]
    end
    
    subgraph Server["🖥️ 自建服务器"]
        direction TB
        Nginx[Nginx<br/>:80/:443]
        
        subgraph Docker["🐳 Docker 容器"]
            AuthHub[AuthHub<br/>:8080]
        end
        
        subgraph External["💾 外部数据库"]
            direction TB
            PG[(PostgreSQL<br/>:5432)]
            Redis[(Redis<br/>:6379)]
        end
    end
    
    User -->|HTTPS 请求| Nginx
    Feishu -->|OAuth 回调| Nginx
    Nginx -->|proxy_pass| AuthHub
    
    AuthHub -->|SQL 查询| PG
    AuthHub -->|缓存/订阅| Redis
    
    AuthHub -.->|健康检查| AuthHub
    
    style User fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Nginx fill:#009639,stroke:#005A22,color:#fff
    style AuthHub fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style PG fill:#336791,stroke:#1A3A5A,color:#fff
    style Redis fill:#DC382D,stroke:#8B1F1A,color:#fff
```

## 🔌 数据库连接方式

```mermaid
%%{init: {'theme':'dark'}}%%
graph TB
    Container[AuthHub 容器<br/>172.17.0.x]
    
    subgraph Options["📡 连接选项"]
        Option1[选项 1:<br/>宿主机内网 IP<br/>192.168.1.100]
        Option2[选项 2:<br/>Docker 网桥<br/>172.17.0.1]
        Option3[选项 3:<br/>host.docker.internal<br/>仅 Mac/Windows]
        Option4[选项 4:<br/>外部服务器 IP<br/>10.0.0.100]
    end
    
    Container --> Option1
    Container --> Option2
    Container --> Option3
    Container --> Option4
    
    Option1 --> DB1[(PostgreSQL<br/>宿主机同一服务器)]
    Option2 --> DB1
    Option3 --> DB1
    Option4 --> DB2[(PostgreSQL<br/>独立数据库服务器)]
    
    style Container fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Option1 fill:#34A853,stroke:#1F6E34,color:#fff
    style Option2 fill:#34A853,stroke:#1F6E34,color:#fff
    style Option3 fill:#FBBC04,stroke:#B87E00,color:#fff
    style Option4 fill:#34A853,stroke:#1F6E34,color:#fff
    style DB1 fill:#336791,stroke:#1A3A5A,color:#fff
    style DB2 fill:#336791,stroke:#1A3A5A,color:#fff
```

## 🔐 飞书 SSO 认证流程

```mermaid
%%{init: {'theme':'dark'}}%%
sequenceDiagram
    participant U as 👤 用户浏览器
    participant A as AuthHub
    participant F as 飞书开放平台
    
    U->>A: 1. 访问前端页面
    A-->>U: 2. 返回页面 & 检查登录状态
    
    Note over U: 未登录
    
    U->>A: 3. 点击登录按钮<br/>GET /api/auth/feishu/login
    A-->>U: 4. 重定向到飞书授权页<br/>带上 redirect_uri
    
    U->>F: 5. 访问飞书授权页
    F-->>U: 6. 显示授权确认页面
    
    U->>F: 7. 用户确认授权
    F-->>U: 8. 重定向回 AuthHub<br/>callback?code=xxx
    
    U->>A: 9. GET /api/auth/feishu/callback?code=xxx
    A->>F: 10. 用 code 换取 access_token
    F-->>A: 11. 返回 access_token
    
    A->>F: 12. 用 access_token 获取用户信息
    F-->>A: 13. 返回用户信息
    
    Note over A: 创建/更新用户<br/>查询用户权限<br/>生成 JWT Token
    
    A-->>U: 14. 设置 Cookie/返回 Token<br/>重定向到首页
    
    U->>A: 15. 后续请求带上 Token<br/>Authorization: Bearer xxx
    A-->>U: 16. 验证 Token<br/>返回数据
    
    Note over A: Token 包含完整权限信息<br/>本地验证，无需查库
```

## 📦 Docker 镜像构建流程

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart LR
    subgraph Stage1["第一阶段: 构建前端"]
        S1_Start[Node.js 20] --> S1_Install[安装依赖<br/>pnpm install]
        S1_Install --> S1_Build[构建前端<br/>pnpm build]
        S1_Build --> S1_Output[输出 dist/]
    end
    
    subgraph Stage2["第二阶段: 构建后端"]
        S2_Start[Python 3.11] --> S2_UV[安装 uv]
        S2_UV --> S2_Install[安装依赖<br/>uv pip install]
        S2_Install --> S2_Copy[复制后端代码]
        S2_Copy --> S2_Frontend[复制前端构建产物]
    end
    
    S1_Output -.->|COPY --from=frontend| S2_Frontend
    
    S2_Frontend --> Final[最终镜像<br/>Backend + Frontend]
    
    style S1_Build fill:#FBBC04,stroke:#B87E00,color:#fff
    style S2_Install fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Final fill:#34A853,stroke:#1F6E34,color:#fff
```

## 🔄 配置更新传播流程

```mermaid
%%{init: {'theme':'dark'}}%%
sequenceDiagram
    participant Admin as 👤 管理员
    participant UI as AuthHub 管理后台
    participant API as AuthHub API
    participant DB as PostgreSQL
    participant Redis as Redis PubSub
    participant SDK as 业务系统 SDK
    
    Admin->>UI: 1. 修改权限配置
    UI->>API: 2. POST /api/rbac/roles
    
    API->>DB: 3. 更新数据库
    DB-->>API: 4. 更新成功
    
    API->>Redis: 5. 发布配置变更通知<br/>PUBLISH config:update
    API-->>UI: 6. 返回成功
    
    Note over Redis,SDK: Redis PubSub 通知
    
    Redis-->>SDK: 7. 收到配置变更通知
    SDK->>API: 8. 拉取最新配置<br/>GET /api/rbac/config
    API->>DB: 9. 查询最新配置
    DB-->>API: 10. 返回配置
    API-->>SDK: 11. 返回最新配置
    
    Note over SDK: 更新本地缓存<br/>1-2秒内生效
    
    SDK-->>SDK: 12. 使用新配置验证权限
```

## 🔧 故障排查流程

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart TD
    Start([服务异常]) --> CheckHealth{健康检查}
    
    CheckHealth -->|失败| CheckContainer{容器运行?}
    CheckHealth -->|成功| CheckAPI{API 响应?}
    
    CheckContainer -->|未运行| CheckLogs[查看容器日志<br/>docker logs]
    CheckContainer -->|运行中| CheckProcess[进入容器检查<br/>docker exec]
    
    CheckLogs --> LogAnalysis{日志分析}
    LogAnalysis -->|数据库错误| DBTrouble[数据库连接故障]
    LogAnalysis -->|Redis错误| RedisTrouble[Redis 连接故障]
    LogAnalysis -->|启动错误| ConfigTrouble[配置文件问题]
    
    DBTrouble --> TestDB[测试数据库连接<br/>psql 命令]
    RedisTrouble --> TestRedis[测试 Redis 连接<br/>redis-cli]
    ConfigTrouble --> CheckEnv[检查 .env 配置]
    
    TestDB --> FixDB{能连接?}
    TestRedis --> FixRedis{能连接?}
    CheckEnv --> FixConfig[修复配置]
    
    FixDB -->|否| NetworkCheck[检查网络<br/>ping/telnet]
    FixDB -->|是| CheckCred[检查凭据]
    
    FixRedis -->|否| NetworkCheck
    FixRedis -->|是| CheckCred
    
    NetworkCheck --> FixNetwork[修复网络问题]
    CheckCred --> UpdateCred[更新凭据]
    
    FixNetwork --> Restart[重启服务]
    UpdateCred --> Restart
    FixConfig --> Restart
    
    CheckAPI -->|异常| CheckNginx[检查 Nginx 配置]
    CheckAPI -->|正常| BusinessCheck[检查业务逻辑]
    
    CheckNginx --> FixNginx[修复反向代理]
    FixNginx --> TestAgain[再次测试]
    
    BusinessCheck --> CheckDB2[检查数据库数据]
    CheckDB2 --> DataFix[修复数据问题]
    
    Restart --> Verify{验证修复}
    TestAgain --> Verify
    DataFix --> Verify
    
    Verify -->|成功| Done([问题解决✅])
    Verify -->|失败| EscalateSupport[联系技术支持]
    
    style Start fill:#EA4335,stroke:#A52E24,color:#fff
    style Done fill:#34A853,stroke:#1F6E34,color:#fff
    style CheckHealth fill:#FBBC04,stroke:#B87E00,color:#fff
    style Verify fill:#FBBC04,stroke:#B87E00,color:#fff
```

## 📊 监控指标

### 应用层监控

```mermaid
%%{init: {'theme':'dark'}}%%
graph TB
    subgraph Metrics["📈 监控指标"]
        direction TB
        
        subgraph API["API 层"]
            API1[请求响应时间]
            API2[请求成功率]
            API3[并发连接数]
            API4[错误率]
        end
        
        subgraph DB["数据库层"]
            DB1[连接池使用率]
            DB2[查询响应时间]
            DB3[慢查询数量]
            DB4[死锁/阻塞]
        end
        
        subgraph Cache["缓存层"]
            Cache1[命中率]
            Cache2[内存使用率]
            Cache3[键数量]
            Cache4[失效率]
        end
        
        subgraph System["系统层"]
            Sys1[CPU 使用率]
            Sys2[内存使用率]
            Sys3[磁盘 I/O]
            Sys4[网络流量]
        end
    end
    
    Metrics --> Alert{告警规则}
    Alert -->|超阈值| Notify[📧 告警通知]
    
    style API fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style DB fill:#336791,stroke:#1A3A5A,color:#fff
    style Cache fill:#DC382D,stroke:#8B1F1A,color:#fff
    style System fill:#34A853,stroke:#1F6E34,color:#fff
    style Notify fill:#EA4335,stroke:#A52E24,color:#fff
```

## 🔄 更新部署流程

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart TD
    Start([开始更新]) --> Backup[1. 备份数据<br/>数据库+密钥+配置]
    Backup --> Pull[2. 拉取最新代码<br/>git pull]
    
    Pull --> CheckChange{3. 检查变更}
    CheckChange -->|有数据库迁移| Migration[4a. 运行迁移<br/>alembic upgrade head]
    CheckChange -->|有配置变更| UpdateEnv[4b. 更新 .env]
    CheckChange -->|无特殊变更| Build[5. 重新构建]
    
    Migration --> Build
    UpdateEnv --> Build
    
    Build[5. 重新构建镜像<br/>docker-compose build]
    Build --> Stop[6. 停止服务<br/>docker-compose down]
    
    Stop --> Deploy[7. 启动新版本<br/>docker-compose up -d]
    Deploy --> Wait[8. 等待启动]
    
    Wait --> Health{9. 健康检查}
    Health -->|失败| Rollback[10a. 回滚<br/>恢复备份]
    Health -->|成功| Verify[10b. 功能验证]
    
    Rollback --> Investigate[调查问题]
    Verify --> Success{验证通过?}
    
    Success -->|否| Rollback
    Success -->|是| Done([更新完成✅])
    
    style Start fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Done fill:#34A853,stroke:#1F6E34,color:#fff
    style Rollback fill:#EA4335,stroke:#A52E24,color:#fff
    style Health fill:#FBBC04,stroke:#B87E00,color:#fff
```

## 相关文档

- [快速部署指南](./QUICKSTART.md)
- [完整部署指南](./self-hosted-deployment.md)
- [部署文档首页](./README.md)
- [架构设计](../architecture/overview.md)

---

**提示**: 所有流程图使用 Mermaid 语法，支持暗色主题，可直接在 Markdown 查看器中渲染。

