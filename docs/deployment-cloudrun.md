# AuthHub Google Cloud Run 部署指南

本此部署方案采用 **前后端一体化容器** 模式，将 React 前端构建为静态资源，由 FastAPI 后端直接托管。适用于 Cloud Run 等无服务器环境。

## 1. 前置准备

### 1.1 基础环境
*   已安装 [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
*   已创建 Google Cloud 项目
*   **外部依赖服务**（需自行维护）：
    *   **PostgreSQL 数据库**: 需确保 Cloud Run 可以访问（公网 IP 或通过 VPC 连接）。
    *   **Redis**: 用于缓存和 Pub/Sub，需确保 Cloud Run 可以访问。

### 1.2 启用必要的 Google Cloud API
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
```

## 2. 环境变量配置

在部署前，请准备好以下环境变量：

| 变量名 | 示例/说明 | 必填 |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db_name` <br>⚠️ **注意**: `postgresql://` 而非 `postgresql+asyncpg://` (Alembic兼容性) | 是 |
| `REDIS_URL` | `redis://host:6379/0` | 是 |
| `FEISHU_APP_ID` | 飞书应用 ID | 是 |
| `FEISHU_APP_SECRET` | 飞书应用 Secret | 是 |
| `FEISHU_ENCRYPT_KEY` | 飞书事件订阅解密 Key | 否 |
| `FEISHU_VERIFICATION_TOKEN` | 飞书事件订阅验证 Token | 否 |
| `APP_NAME` | `AuthHub-Cloud` | 否 |
| `LOG_LEVEL` | `INFO` | 否 |

---

## 3. 构建镜像

使用 Cloud Build 构建 Docker 镜像并推送到 Google Container Registry (GCR) 或 Artifact Registry。

```bash
# 设置项目 ID
export PROJECT_ID="your-project-id"

# 提交构建
gcloud builds submit --tag gcr.io/$PROJECT_ID/authhub:latest .
```

---

## 4. 密钥管理 (Google Secret Manager) - **强烈推荐**

为了防止每次部署或扩缩容时 JWT 密钥丢失导致用户登录失效，**必须**使用 Google Secret Manager 管理 RSA 密钥并挂载到容器中。

### 4.1 本地生成密钥
如果在本地还没有密钥，请先生成：
```bash
cd backend
# 这会在 backend/keys/ 目录下生成 private_key.pem 和 public_key.pem
python scripts/generate_keys.py
cd ..
```

### 4.2 上传密钥到 Secret Manager
创建两个 Secret 来分别存储私钥和公钥。

```bash
# 1. 创建私钥 Secret
gcloud secrets create authhub-private-key \
    --data-file=backend/keys/private_key.pem \
    --replication-policy=automatic

# 2. 创建公钥 Secret
gcloud secrets create authhub-public-key \
    --data-file=backend/keys/public_key.pem \
    --replication-policy=automatic
```

### 4.3 授予权限
Cloud Run 默认使用 Compute Engine 默认服务账号。你需要授予该账号读取 Secret 的权限。

```bash
# 1. 获取项目编号 (Project Number)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 2. 授予 Secret Accessor 权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## 5. 部署到 Cloud Run

使用 `--set-secrets` 参数将 Secret 挂载为文件。

```bash
gcloud run deploy authhub \
  --image gcr.io/$PROJECT_ID/authhub:latest \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "DATABASE_URL=postgresql://user:password@db-host:5432/authhub" \
  --set-env-vars "REDIS_URL=redis://redis-host:6379/0" \
  --set-env-vars "FEISHU_APP_ID=cli_xxx" \
  --set-env-vars "FEISHU_APP_SECRET=xxx" \
  --set-secrets "/app/keys/private_key.pem=authhub-private-key:latest" \
  --set-secrets "/app/keys/public_key.pem=authhub-public-key:latest"
```

### 参数说明
*   `--set-secrets "/app/keys/private_key.pem=authhub-private-key:latest"`: 
    *   **目标路径** (`/app/keys/private_key.pem`): 容器内文件路径，需与代码配置一致。
    *   **源 Secret** (`authhub-private-key:latest`): Secret Manager 中的名称和版本。
*   **启动逻辑**: 容器启动脚本 (`docker-entrypoint.sh`) 会检测到这些文件已存在，从而**跳过**自动生成步骤，确保使用你上传的固定密钥。

---

## 6. 运维与更新

### 更新应用
代码修改后，重复执行 **3. 构建镜像** 和 **5. 部署** 步骤即可。Cloud Run 会自动进行蓝绿部署。

### 查看日志
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=authhub" --limit 50
```