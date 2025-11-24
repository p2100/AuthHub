#!/bin/bash
# AuthHub 生产环境快速部署脚本（使用外部数据库）

set -e

echo "🚀 AuthHub 生产环境部署脚本"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ 请不要使用 root 用户运行此脚本${NC}"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    echo "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境检查通过${NC}"
echo ""

# 创建 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 创建 .env 配置文件...${NC}"
    cat > .env << 'EOF'
# ==================== 应用配置 ====================
APP_NAME=AuthHub
DEBUG=false
HOST=0.0.0.0
PORT=8080

# ==================== 外部数据库配置 ====================
# PostgreSQL 连接 URL（使用外部数据库的实际地址）
DATABASE_URL=postgresql://authhub:CHANGE_ME@your-db-host:5432/authhub

# ==================== 外部 Redis 配置 ====================
# Redis 连接 URL（使用外部 Redis 的实际地址）
REDIS_URL=redis://:CHANGE_ME@your-redis-host:6379/0

# ==================== JWT配置 ====================
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_PRIVATE_KEY_PATH=/app/keys/private_key.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public_key.pem

# ==================== 飞书配置 ====================
FEISHU_APP_ID=CHANGE_ME
FEISHU_APP_SECRET=CHANGE_ME
FEISHU_ENCRYPT_KEY=
FEISHU_VERIFICATION_TOKEN=

# ==================== CORS配置 ====================
CORS_ORIGINS=["https://your-domain.com"]

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ .env 文件已创建${NC}"
    echo -e "${YELLOW}⚠️  请编辑 .env 文件，填写正确的配置信息${NC}"
    echo ""
else
    echo -e "${GREEN}✅ .env 文件已存在${NC}"
    echo ""
fi

# 生成 RSA 密钥
if [ ! -f keys/private_key.pem ]; then
    echo -e "${YELLOW}🔑 生成 RSA 密钥对...${NC}"
    mkdir -p keys
    
    # 检查是否有 Python 环境
    if command -v python3 &> /dev/null; then
        cd backend
        python3 scripts/generate_keys.py
        cd ..
        echo -e "${GREEN}✅ RSA 密钥生成成功${NC}"
    else
        # 使用 OpenSSL 生成
        echo -e "${YELLOW}使用 OpenSSL 生成密钥...${NC}"
        openssl genrsa -out keys/private_key.pem 2048
        openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
        echo -e "${GREEN}✅ RSA 密钥生成成功${NC}"
    fi
    echo ""
else
    echo -e "${GREEN}✅ RSA 密钥已存在${NC}"
    echo ""
fi

# 检查 .env 配置
echo -e "${YELLOW}📋 检查配置文件...${NC}"
if grep -q "CHANGE_ME" .env; then
    echo -e "${RED}❌ .env 文件中仍有 CHANGE_ME 占位符${NC}"
    echo -e "${YELLOW}请编辑 .env 文件，填写以下配置：${NC}"
    echo "  1. DATABASE_URL - PostgreSQL 连接字符串"
    echo "  2. REDIS_URL - Redis 连接字符串"
    echo "  3. FEISHU_APP_ID - 飞书应用 ID"
    echo "  4. FEISHU_APP_SECRET - 飞书应用 Secret"
    echo "  5. CORS_ORIGINS - 允许的跨域来源"
    echo ""
    echo "编辑完成后，再次运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ 配置检查通过${NC}"
echo ""

# 询问是否继续
echo -e "${YELLOW}准备构建并启动 AuthHub 服务${NC}"
read -p "是否继续? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消部署"
    exit 0
fi

# 构建镜像
echo ""
echo -e "${YELLOW}🔨 构建 Docker 镜像...${NC}"
docker-compose -f docker-compose-production.yml build

# 启动服务
echo ""
echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose -f docker-compose-production.yml up -d

# 等待服务启动
echo ""
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo ""
echo -e "${YELLOW}📊 检查服务状态...${NC}"
docker-compose -f docker-compose-production.yml ps

# 检查健康状态
echo ""
echo -e "${YELLOW}🏥 检查服务健康状态...${NC}"
if curl -f http://localhost:${PORT:-8080}/health &> /dev/null; then
    echo -e "${GREEN}✅ 服务健康检查通过！${NC}"
else
    echo -e "${RED}❌ 服务健康检查失败${NC}"
    echo "查看日志: docker-compose -f docker-compose-production.yml logs -f"
    exit 1
fi

# 部署完成
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "服务地址:"
echo "  - API 文档: http://localhost:${PORT:-8080}/docs"
echo "  - 健康检查: http://localhost:${PORT:-8080}/health"
echo ""
echo "常用命令:"
echo "  - 查看日志: docker-compose -f docker-compose-production.yml logs -f"
echo "  - 停止服务: docker-compose -f docker-compose-production.yml down"
echo "  - 重启服务: docker-compose -f docker-compose-production.yml restart"
echo "  - 查看状态: docker-compose -f docker-compose-production.yml ps"
echo ""
echo "下一步:"
echo "  1. 配置 Nginx 反向代理（参考文档）"
echo "  2. 配置 SSL 证书"
echo "  3. 在飞书后台配置回调地址: https://your-domain.com/api/auth/feishu/callback"
echo "  4. 配置防火墙规则"
echo ""
echo "文档: docs/deployment/self-hosted-deployment.md"
echo ""

