# Cloud Run 连接自建数据库方案对比

本文档详细分析了在 Cloud Run 环境下连接外部自建数据库（如 VPS 上的 PostgreSQL）的两种主要方案：**安全连接方案（静态 IP）** 与 **低成本方案（公网直连）**，并对成本和安全性进行了对比。

## 方案一：企业级安全连接 (VPC + Cloud NAT)

通过 GCP 网络组件为 Cloud Run 构建固定出口 IP，从而实现数据库防火墙的精确白名单控制。

### 架构原理
`Cloud Run` -> `VPC Connector` -> `Cloud Router` -> `Cloud NAT` -> `Static IP` -> `VPS Database`

### 成本预估 (以 asia-east2 为例)
| 组件 | 计费项 | 预估月成本 (USD) | 说明 |
| :--- | :--- | :--- | :--- |
| **Serverless VPC Connector** | 实例运行时长 | **$15 ~ $25** | 最小配置通常需 2 个实例常驻，即便无流量也计费。 |
| **Cloud NAT** | 网关租用 + 流量处理 | **$32+** | 网关小时费约 $0.044/hr，另加流量费 $0.045/GB。 |
| **Static IP** | IP 保留费用 | **$3 ~ $4** | 绑定 NAT 使用时通常有优惠，但可能产生少量费用。 |
| **总计** | | **~$50 - $60 / 月** | 适合预算充足、对安全有严格要求的生产环境。 |

### 优点
*   **最高安全性**: 数据库防火墙仅需放行一个 IP。
*   **标准合规**: 符合企业级安全审计要求。
*   **网络稳定**: 走 GCP 骨干网路由，延迟更可控。

### 缺点
*   **成本高**: 对于个人项目或小流量应用，基础设施费用昂贵。
*   **配置复杂**: 涉及 VPC、Subnet、Router、NAT 等多个网络组件配置。

---

## 方案二：低成本公网直连 (推荐用于个人/初创项目)

直接利用 Cloud Run 的公网连接能力访问数据库，依靠数据库自身的认证机制保障安全。

### 架构原理
`Cloud Run (动态 IP)` -> `公网 (Internet)` -> `VPS Database`

### 成本
*   **$0 (零额外成本)**

### 安全配置指南 (弥补无 IP 白名单的风险)
由于无法限制来源 IP，必须在其他层面加强安全：

1.  **强密码策略**: 数据库用户密码必须是高强度随机字符串（20位以上，含特殊字符）。
2.  **强制 SSL/TLS**:
    *   配置 PostgreSQL `pg_hba.conf` 强制要求 SSL 连接 (`hostssl`)。
    *   防止中间人攻击和数据窃听。
3.  **非标准端口 (可选)**:
    *   将数据库端口从默认的 `5432` 改为其他高位端口（如 `54321`），减少自动化扫描脚本的骚扰。
4.  **权限最小化**:
    *   专为 AuthHub 创建数据库用户。
    *   仅授予 `authhub` 数据库的读写权限，**严禁** 授予 `SUPERUSER` 或 `Replication` 权限。
5.  **Fail2Ban (VPS侧)**:
    *   在 VPS 上配置 Fail2Ban，监控 PostgreSQL 日志，自动封禁多次认证失败的 IP。

### 优点
*   **零成本**: 无需购买任何 GCP 网络组件。
*   **简单**: 无需配置复杂的 VPC 网络。

### 缺点
*   **攻击面暴露**: 数据库端口对全网开放，容易遭受暴力破解攻击（虽然强密码可以防御，但会消耗资源）。

---

## 决策建议

| 场景 | 推荐方案 | 理由 |
| :--- | :--- | :--- |
| **个人学习 / 原型开发** | **方案二** | 没必要为网络组件支付比服务器还贵的费用。 |
| **初创项目 / 内部工具** | **方案二 + 强安全配置** | 只要密码足够强且启用了 SSL，风险是可控的。 |
| **企业核心业务 / 存有敏感数据** | **方案一** | 数据安全高于一切，必须通过网络隔离和白名单进行多层防护。 |
| **预算敏感但不想运维数据库** | **方案三 (Serverless DB)** | 迁移到 Neon、Supabase 等云数据库，它们自带 HTTP 连接池或针对 Serverless 优化的连接方式，通常有免费层级。 |

## 附录：方案一配置命令参考

如果决定采用方案一，请按顺序执行以下命令：

```bash
# 1. 创建 VPC 连接器
gcloud compute networks vpc-access connectors create authhub-connector \
  --network default --region asia-east2 --range 10.8.0.0/28

# 2. 创建静态 IP
gcloud compute addresses create authhub-static-ip --region asia-east2

# 3. 创建 Cloud Router
gcloud compute routers create authhub-router --network default --region asia-east2

# 4. 创建 NAT 网关
gcloud compute routers nats create authhub-nat \
  --router authhub-router --region asia-east2 \
  --nat-all-subnet-ip-ranges --nat-external-ip-pool authhub-static-ip

# 5. 部署时绑定
gcloud run deploy ... --vpc-connector authhub-connector --vpc-egress all-traffic
```
