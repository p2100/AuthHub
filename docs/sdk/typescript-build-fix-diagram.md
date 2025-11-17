# TypeScript SDK 构建修复流程图

## 问题与修复流程

```mermaid
%%{init: {'theme':'dark','themeVariables': {'primaryColor':'#BB2528','primaryTextColor':'#fff','primaryBorderColor':'#7C0000','lineColor':'#F8B229','secondaryColor':'#006100','tertiaryColor':'#fff'}}}%%
flowchart TB
    Start([运行发布脚本]) --> Problem1{ESLint 配置缺失}
    Start --> Problem2{Jest 测试失败}
    Start --> Problem3{构建失败}
    
    Problem1 -->|创建配置| Fix1[添加 .eslintrc.json]
    Problem2 -->|添加配置| Fix2[创建 jest.config.js<br/>设置 passWithNoTests]
    
    Problem3 --> Issue3A{类型导出错误}
    Problem3 --> Issue3B{AuthClient 不完整}
    Problem3 --> Issue3C{Vue/React 依赖问题}
    Problem3 --> Issue3D{TypeScript 类型错误}
    
    Issue3A -->|修正路径| Fix3A[修改 index.ts<br/>从 types.ts 导出]
    Issue3B -->|添加方法| Fix3B[实现 getCurrentUser<br/>login/logout 方法]
    Issue3C -->|标记为外部| Fix3C[build 脚本添加<br/>--external react vue]
    Issue3D -->|完善定义| Fix3D[修复 types.ts<br/>添加可选属性处理]
    
    Fix1 --> Verify1[✅ Lint 通过]
    Fix2 --> Verify2[✅ Test 通过]
    Fix3A --> Verify3
    Fix3B --> Verify3
    Fix3C --> Verify3
    Fix3D --> Verify3[✅ Build 成功]
    
    Verify1 --> Success
    Verify2 --> Success
    Verify3 --> Success([🎉 发布脚本正常运行])
    
    style Start fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Success fill:#50C878,stroke:#2E7D4E,color:#fff
    style Problem1 fill:#E74C3C,stroke:#C0392B,color:#fff
    style Problem2 fill:#E74C3C,stroke:#C0392B,color:#fff
    style Problem3 fill:#E74C3C,stroke:#C0392B,color:#fff
    style Fix1 fill:#F39C12,stroke:#D68910,color:#fff
    style Fix2 fill:#F39C12,stroke:#D68910,color:#fff
    style Fix3A fill:#F39C12,stroke:#D68910,color:#fff
    style Fix3B fill:#F39C12,stroke:#D68910,color:#fff
    style Fix3C fill:#F39C12,stroke:#D68910,color:#fff
    style Fix3D fill:#F39C12,stroke:#D68910,color:#fff
    style Verify1 fill:#27AE60,stroke:#1E8449,color:#fff
    style Verify2 fill:#27AE60,stroke:#1E8449,color:#fff
    style Verify3 fill:#27AE60,stroke:#1E8449,color:#fff
```

## 类型修复详情

```mermaid
%%{init: {'theme':'dark','themeVariables': {'primaryColor':'#BB2528','primaryTextColor':'#fff','primaryBorderColor':'#7C0000','lineColor':'#F8B229','secondaryColor':'#006100','tertiaryColor':'#fff'}}}%%
classDiagram
    class AuthConfig {
        +string backendUrl
        +string? loginPath
        +string? logoutPath
        +string? mePath
    }
    
    class User {
        +string sub
        +string username
        +string? email
        +string[]? global_roles
        +Record system_roles
        +number[]? dept_ids
        +string[]? dept_names
    }
    
    class TokenPayload {
        +Record? global_resources
        +Record? system_resources
        +number exp
        +number iat
        +string jti
        +string email
        +string[] global_roles
    }
    
    class AuthClient {
        -string backendUrl
        -string loginPath
        -string logoutPath
        -string mePath
        +constructor(config)
        +getCurrentUser() Promise~User~
        +login(returnUrl?) void
        +logout() Promise~void~
        +refreshToken(token) Promise~SSOTokenResponse~
    }
    
    class PermissionConfig {
        +string version
        +Record~RoleConfig~ roles
        +RouteConfig[]? routes
        +RoutePatternConfig[]? route_patterns
    }
    
    class RoleConfig {
        +number id
        +string code
        +string name
        +string[] permissions
    }
    
    class RoutePatternConfig {
        +string pattern
        +string method
        +string role
        +number priority
    }
    
    User <|-- TokenPayload
    AuthClient ..> User : 返回
    AuthClient ..> AuthConfig : 使用
    PermissionConfig *-- RoleConfig
    PermissionConfig *-- RoutePatternConfig
    
    note for AuthClient "✨ 新增方法:\n- getCurrentUser()\n- login()\n- logout()"
    note for RoleConfig "🔧 修复:\npermissions 改为 string[]"
    note for PermissionConfig "🔧 修复:\n添加 route_patterns 属性"
```

## 构建流程

```mermaid
%%{init: {'theme':'dark','themeVariables': {'primaryColor':'#BB2528','primaryTextColor':'#fff','primaryBorderColor':'#7C0000','lineColor':'#F8B229','secondaryColor':'#006100','tertiaryColor':'#fff'}}}%%
graph LR
    A[源代码<br/>src/] --> B{tsup}
    B -->|--external react| C1[CJS Build]
    B -->|--external vue| C2[ESM Build]
    B -->|--dts| C3[DTS Build]
    
    C1 --> D1[dist/index.js<br/>10KB]
    C2 --> D2[dist/index.mjs<br/>7.9KB]
    C3 --> D3[dist/index.d.ts<br/>6.3KB]
    C3 --> D4[dist/index.d.mts<br/>6.3KB]
    
    D1 --> E[📦 发布到 npm]
    D2 --> E
    D3 --> E
    D4 --> E
    
    style A fill:#3498DB,stroke:#2E86C1,color:#fff
    style B fill:#9B59B6,stroke:#7D3C98,color:#fff
    style C1 fill:#E67E22,stroke:#CA6F1E,color:#fff
    style C2 fill:#E67E22,stroke:#CA6F1E,color:#fff
    style C3 fill:#E67E22,stroke:#CA6F1E,color:#fff
    style D1 fill:#1ABC9C,stroke:#16A085,color:#fff
    style D2 fill:#1ABC9C,stroke:#16A085,color:#fff
    style D3 fill:#1ABC9C,stroke:#16A085,color:#fff
    style D4 fill:#1ABC9C,stroke:#16A085,color:#fff
    style E fill:#27AE60,stroke:#229954,color:#fff
```

## 修复前后对比

| 问题 | 修复前 | 修复后 |
|------|--------|--------|
| **ESLint** | ❌ 找不到配置文件 | ✅ 配置完整,可正常运行 |
| **Jest** | ❌ 无测试时失败 | ✅ `passWithNoTests: true` |
| **类型导出** | ❌ 从错误模块导出 | ✅ 从 `types.ts` 正确导出 |
| **AuthClient** | ❌ 缺少关键方法 | ✅ 实现完整的前端 API |
| **React/Vue** | ❌ 尝试打包进 bundle | ✅ 标记为 external |
| **RoleConfig.permissions** | ❌ `PermissionItem[]` | ✅ `string[]` |
| **PermissionConfig** | ❌ 缺少 `route_patterns` | ✅ 添加可选属性 |
| **可选属性处理** | ❌ 直接访问可能 undefined | ✅ 添加空值检查 |
| **构建结果** | ❌ 构建失败 | ✅ 成功生成 4 个文件 |

## 关键代码变更

### 1. AuthClient 构造函数

```typescript
// 修复前
constructor(authhubUrl: string)

// 修复后
constructor(config: string | AuthConfig) // 支持两种方式
```

### 2. 可选属性处理

```typescript
// 修复前
const userRoles = tokenPayload.system_roles[this.namespace] || [];

// 修复后
const systemRoles = tokenPayload.system_roles || {};
const userRoles = systemRoles[this.namespace] || [];
```

### 3. 构建命令

```bash
# 修复前
tsup src/index.ts --format cjs,esm --dts

# 修复后
tsup src/index.ts --format cjs,esm --dts --external react --external vue
```

