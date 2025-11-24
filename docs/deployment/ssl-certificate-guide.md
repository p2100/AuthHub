# SSL 证书配置指南

本指南介绍如何为 AuthHub 配置 SSL 证书，包括 Cloudflare、Let's Encrypt 等多种方式。

## 📋 目录

- [方式一：Cloudflare（推荐）](#方式一cloudflare推荐)
- [方式二：Let's Encrypt](#方式二lets-encrypt)
- [方式三：自签名证书（仅测试）](#方式三自签名证书仅测试)
- [证书更新和续期](#证书更新和续期)

## 方式一：Cloudflare（推荐）

Cloudflare 提供**免费的 SSL 证书**，支持自动续期，配置简单。

### 🎯 部署架构

```mermaid
%%{init: {'theme':'dark'}}%%
graph LR
    User[👤 用户] -->|HTTPS| CF[Cloudflare CDN<br/>SSL 终止]
    CF -->|HTTP/HTTPS| Server[自建服务器<br/>Nginx]
    Server -->|HTTP| AuthHub[AuthHub 容器<br/>:8080]
    
    style User fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style CF fill:#F38020,stroke:#C26519,color:#fff
    style Server fill:#009639,stroke:#005A22,color:#fff
    style AuthHub fill:#4A90E2,stroke:#2E5C8A,color:#fff
```

### 选项 A：使用 Cloudflare 作为反向代理（最简单）

#### 1. 添加域名到 Cloudflare

1. 注册 [Cloudflare](https://www.cloudflare.com/) 账号（免费）
2. 添加你的域名
3. 修改域名的 DNS 服务器为 Cloudflare 提供的地址

#### 2. 配置 DNS 记录

在 Cloudflare DNS 面板中添加 A 记录：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|----------|
| A | @ | 你的服务器IP | ✅ 已代理 |
| A | www | 你的服务器IP | ✅ 已代理 |

> **重要**: 确保"代理状态"为**橙色云朵图标**（已代理），这样流量会经过 Cloudflare，自动获得 SSL。

#### 3. 配置 SSL/TLS 模式

在 Cloudflare 面板中：

**SSL/TLS** → **概述** → 选择加密模式：

- **灵活（Flexible）**: Cloudflare ↔ 服务器使用 HTTP（不推荐）
- **完全（Full）**: Cloudflare ↔ 服务器使用 HTTPS，但不验证证书
- **完全（严格）（Full Strict）**: Cloudflare ↔ 服务器使用 HTTPS，验证证书（推荐）

#### 4. 配置 Nginx（灵活模式）

如果选择**灵活模式**，Nginx 不需要配置证书：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 真实 IP 获取（重要！）
    real_ip_header CF-Connecting-IP;
    set_real_ip_from 0.0.0.0/0;
    
    # 日志配置
    access_log /var/log/nginx/authhub-access.log;
    error_log /var/log/nginx/authhub-error.log;
    
    # 客户端上传限制
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8080;  # 使用 127.0.0.1 而不是 localhost
        proxy_http_version 1.1;
        
        # 请求头配置
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        access_log off;
    }
}
```

#### 5. 重载 Nginx

```bash
# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

✅ **完成！** 现在访问 `https://your-domain.com` 即可，Cloudflare 自动提供 SSL 加密。

### 选项 B：使用 Cloudflare Origin CA 证书（推荐）

更安全的方式，使用 **Cloudflare Origin CA** 证书保护 Cloudflare 到服务器的连接。

#### 1. 生成 Origin CA 证书

在 Cloudflare 面板：

1. **SSL/TLS** → **源服务器** → **创建证书**
2. 选择：
   - 私钥类型：**RSA (2048)**
   - 主机名：`your-domain.com` 和 `*.your-domain.com`
   - 证书有效期：**15 年**
3. 点击**创建**

#### 2. 保存证书

复制生成的证书和私钥：

```bash
# 创建证书目录
sudo mkdir -p /etc/nginx/ssl

# 保存证书（复制 Origin Certificate）
sudo tee /etc/nginx/ssl/cloudflare-origin.crt > /dev/null << 'EOF'
-----BEGIN CERTIFICATE-----
粘贴 Cloudflare 提供的 Origin Certificate
-----END CERTIFICATE-----
EOF

# 保存私钥（复制 Private key）
sudo tee /etc/nginx/ssl/cloudflare-origin.key > /dev/null << 'EOF'
-----BEGIN PRIVATE KEY-----
粘贴 Cloudflare 提供的 Private key
-----END PRIVATE KEY-----
EOF

# 设置权限
sudo chmod 600 /etc/nginx/ssl/cloudflare-origin.key
sudo chmod 644 /etc/nginx/ssl/cloudflare-origin.crt
```

#### 3. 配置 Nginx（推荐配置 - 避免重定向循环）

```nginx
# /etc/nginx/conf.d/authhub.conf
# 或 /etc/nginx/sites-available/authhub

server {
    listen 80;
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;  # 改为你的域名
    
    # Cloudflare Origin CA 证书
    ssl_certificate /etc/nginx/ssl/cloudflare-origin.crt;
    ssl_certificate_key /etc/nginx/ssl/cloudflare-origin.key;
    
    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 真实 IP 获取（重要！）
    real_ip_header CF-Connecting-IP;
    set_real_ip_from 0.0.0.0/0;
    
    # 日志配置
    access_log /var/log/nginx/authhub-access.log;
    error_log /var/log/nginx/authhub-error.log;
    
    # 客户端上传限制
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8080;  # 使用 127.0.0.1 而不是 localhost
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
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        access_log off;
    }
    
    # 静态资源缓存（如果前端也部署在这里）
    location /static {
        proxy_pass http://127.0.0.1:8080/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

> **重要说明**:
> - ✅ 同时监听 80 和 443 端口，避免重定向循环
> - ✅ 使用 `127.0.0.1` 而不是 `localhost`，避免 DNS 解析问题
> - ✅ 不要在 Nginx 层面做 HTTP 到 HTTPS 的跳转（由 Cloudflare 处理）
> - ✅ 确保 Cloudflare 的 "始终使用 HTTPS" 功能已开启

#### 4. 配置 Cloudflare SSL 模式

在 Cloudflare 面板中：

1. **SSL/TLS** → **概述** → 选择 **完全（严格）**
2. **SSL/TLS** → **边缘证书** → 开启 **始终使用 HTTPS**

这样配置后：
- ✅ 用户到 Cloudflare：HTTPS 加密
- ✅ Cloudflare 到服务器：HTTPS 加密（验证 Origin CA 证书）
- ✅ Cloudflare 自动将 HTTP 请求跳转到 HTTPS
- ✅ Nginx 不需要处理重定向，避免循环

#### 5. 重载 Nginx

```bash
# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### Cloudflare 额外优化

#### 1. 启用 HTTP/3（QUIC）

**速度** → **优化** → **HTTP/3（带 QUIC）** → 开启

#### 2. 启用 Brotli 压缩

**速度** → **优化** → **Brotli** → 开启

#### 3. 配置缓存规则

**缓存** → **配置** → 创建页面规则：

```
URL: https://your-domain.com/static/*
设置: 缓存级别 - 缓存所有内容
浏览器缓存 TTL: 1 年
```

#### 4. 防火墙规则（可选）

**安全性** → **WAF** → **创建防火墙规则**

保护后台管理页面：

```
如果 URL 包含 /admin
且 国家/地区 不在 [CN, HK, TW]
则 阻止
```

## 方式二：Let's Encrypt

完全免费的 SSL 证书，自动续期，适合不使用 Cloudflare 的场景。

### 1. 安装 Certbot

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

#### CentOS/RHEL

```bash
sudo yum install -y epel-release
sudo yum install -y certbot python3-certbot-nginx
```

### 2. 获取证书

```bash
# 方式 1: 自动配置 Nginx（推荐）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 方式 2: 仅获取证书
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# 方式 3: 使用 Standalone 模式（需要停止 Nginx）
sudo systemctl stop nginx
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
sudo systemctl start nginx
```

### 3. Nginx 配置

如果使用方式 2 或 3，需要手动配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # ACME 验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # 强制跳转 HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # Let's Encrypt 证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 优化配置（从 Certbot 推荐配置）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS（可选，启用后浏览器强制使用 HTTPS）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 其他配置同上...
    
    location / {
        proxy_pass http://localhost:8080;
        # ... 省略
    }
}
```

### 4. 自动续期

Let's Encrypt 证书有效期 90 天，需要自动续期：

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 添加到 Crontab（每天检查两次）
sudo crontab -e
# 添加以下行
0 0,12 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

## 方式三：自签名证书（仅测试）

⚠️ **仅用于开发测试环境**，生产环境请使用上述方式。

### 1. 生成自签名证书

```bash
# 创建证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成私钥和证书（有效期 365 天）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=YourCompany/OU=IT/CN=your-domain.com"

# 设置权限
sudo chmod 600 /etc/nginx/ssl/selfsigned.key
sudo chmod 644 /etc/nginx/ssl/selfsigned.crt
```

### 2. Nginx 配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # 自签名证书
    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    
    # 其他配置同上...
}
```

### 3. 浏览器信任证书

自签名证书会显示"不安全"警告，需要手动信任：

- Chrome: 访问页面 → 高级 → 继续访问
- 开发环境: 将证书添加到系统信任列表

## 证书更新和续期

### Cloudflare Origin CA

- 有效期：15 年
- 续期：到期前在 Cloudflare 面板重新生成

### Let's Encrypt

- 有效期：90 天
- 自动续期：Certbot 会自动处理
- 手动续期：`sudo certbot renew`

### 检查证书有效期

```bash
# 查看证书到期时间
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates

# Let's Encrypt 证书列表
sudo certbot certificates
```

## 对比和选择

| 方式 | 费用 | 配置难度 | 自动续期 | 推荐场景 |
|------|------|---------|---------|---------|
| **Cloudflare** | 免费 | ⭐️ 简单 | ✅ 自动 | **生产环境（推荐）** |
| **Cloudflare Origin CA** | 免费 | ⭐️⭐️ 中等 | ✅ 15年有效 | **生产环境（更安全）** |
| **Let's Encrypt** | 免费 | ⭐️⭐️⭐️ 复杂 | ✅ 自动 | 不使用 Cloudflare |
| **自签名证书** | 免费 | ⭐️ 简单 | ❌ 手动 | **仅测试环境** |

## 推荐配置

### 1. 小型项目/个人项目

**Cloudflare 灵活模式**（最简单）

- ✅ 零配置即可使用 HTTPS
- ✅ 免费 CDN 加速
- ✅ 免费 DDoS 防护
- ⚠️ Cloudflare 到服务器使用 HTTP

### 2. 企业项目/重要项目

**Cloudflare Origin CA**（推荐）

- ✅ 端到端加密
- ✅ 15 年有效期
- ✅ 免费 CDN 和防护
- ✅ 配置简单

### 3. 无法使用 Cloudflare

**Let's Encrypt**

- ✅ 完全免费
- ✅ 自动续期
- ⚠️ 需要开放 80 端口
- ⚠️ 配置相对复杂

## 常见问题

### Q1: Cloudflare 灵活模式安全吗？

**A**: 用户到 Cloudflare 是 HTTPS 加密的，但 Cloudflare 到服务器是 HTTP。适合公开内容，建议敏感数据使用 **完全（严格）** 模式。

### Q6: 为什么会出现 "重定向次数过多" 错误？

**A**: 常见原因：
1. ❌ Nginx 配置了 HTTP 到 HTTPS 的强制跳转，但 Cloudflare 使用了"灵活"模式
2. ❌ `server_name` 配置错误
3. ✅ **解决方案**: 同时监听 80 和 443 端口，让 Cloudflare 处理 HTTPS 跳转

### Q7: 为什么 Nginx 提示 "host not found in upstream"？

**A**: 使用 `127.0.0.1` 而不是 `localhost`，或者直接在 `proxy_pass` 中使用 IP 地址，避免 DNS 解析问题。

### Q2: Cloudflare 会影响性能吗？

**A**: 不会，反而会提升性能：
- ✅ 全球 CDN 加速
- ✅ 智能路由
- ✅ HTTP/3 支持
- ✅ 压缩优化

### Q5: Let's Encrypt 证书会过期吗？

**A**: 会，有效期 90 天。但 Certbot 会自动续期，无需手动操作。

### Q6: 可以同时使用 Cloudflare 和 Let's Encrypt 吗？

**A**: 可以，但没必要。Cloudflare 已经提供了 SSL，再使用 Let's Encrypt 是多余的。

### Q7: Origin CA 证书可以用在其他地方吗？

**A**: 不可以，Origin CA 证书只能用于 Cloudflare 和你的源服务器之间，浏览器不会信任它。

## 验证 SSL 配置

### 1. 在线测试

- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [SSL Checker](https://www.sslshopper.com/ssl-checker.html)

### 2. 命令行测试

```bash
# 测试 SSL 连接
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# 查看证书信息
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -text

# 测试 HTTP/2
curl -I --http2 https://your-domain.com
```

## 相关文档

- [快速部署指南](./QUICKSTART.md)
- [完整部署指南](./self-hosted-deployment.md)
- [Nginx 配置优化](./nginx-optimization.md)
- [Cloudflare 官方文档](https://developers.cloudflare.com/ssl/)
- [Let's Encrypt 官方文档](https://letsencrypt.org/docs/)

---

**推荐使用 Cloudflare**，配置简单且功能强大！🚀

