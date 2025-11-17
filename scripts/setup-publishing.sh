#!/bin/bash

# AuthHub SDK 发布环境配置脚本
# 这个脚本将帮助你配置发布环境

echo "===== AuthHub SDK 发布环境配置 ====="
echo ""

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查必要工具
log_step "检查必要工具..."

# 检查 uv
if command -v uv &> /dev/null; then
    log_info "uv 已安装: $(uv --version)"
else
    log_warn "uv 未安装"
    echo "安装方法:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 检查 pnpm
if command -v pnpm &> /dev/null; then
    log_info "pnpm 已安装: $(pnpm --version)"
else
    log_warn "pnpm 未安装"
    echo "安装方法:"
    echo "  npm install -g pnpm"
fi

# 检查 Python SDK
if [[ -f "/Users/leo/code/work/AuthHub/sdk/python/pyproject.toml" ]]; then
    log_info "Python SDK 配置: 已存在"
    cd /Users/leo/code/work/AuthHub/sdk/python
    log_info "当前版本: $(grep -E '^version\s*=' pyproject.toml | cut -d'=' -f2 | sed 's/[" ]//g')"
else
    log_warn "Python SDK 配置: 不存在"
fi

# 检查 TypeScript SDK
if [[ -f "/Users/leo/code/work/AuthHub/sdk/typescript/package.json" ]]; then
    log_info "TypeScript SDK 配置: 已存在"
    cd /Users/leo/code/work/AuthHub/sdk/typescript
    log_info "当前版本: $(grep '"version"' package.json | cut -d'"' -f4)"
else
    log_warn "TypeScript SDK 配置: 不存在"
fi

echo ""
echo "======================================"
echo "配置 PyPI 认证"
echo "======================================"

read -p "是否需要配置 PyPI API token? (y/n): " setup_pypi
if [[ "$setup_pypi" == "y" ]]; then
    echo ""
    echo "配置 PyPI API token:"
    echo "1. 访问 https://pypi.org/manage/account/token/"
    echo "2. 点击 'Add API token'"
    echo "3. Token name: 'authhub-sdk-publish-token'"
    echo "4. Scope: 'Entire account (all projects)'"
    echo "5. 复制生成的 token"
    echo ""

    read -p "请粘贴你的 PyPI token: " pypi_token

    if [[ -n "$pypi_token" ]]; then
        # 写入配置文件
        CONFIG_FILE="$HOME/.authhub-pypi-token"
        echo "export UV_PUBLISH_TOKEN='pypi-$pypi_token'" > "$CONFIG_FILE"

        log_info "Token 已保存到: $CONFIG_FILE"
        log_info "使用方式: source $CONFIG_FILE"

        # 立即加载
        export UV_PUBLISH_TOKEN="pypi-$pypi_token"
        log_info "当前会话已加载 token"
    fi
fi

echo ""
echo "======================================"
echo "配置 npm 认证"
echo "======================================"

read -p "是否需要登录 npm? (y/n): " setup_npm
if [[ "$setup_npm" == "y" ]]; then
    log_info "正在启动 npm 登录..."
    pnpm login

    if pnpm whoami &> /dev/null; then
        log_info "登录成功! 当前用户: $(pnpm whoami)"
    else
        log_warn "登录失败"
    fi
fi

echo ""
echo "======================================"
echo "发布指南"
echo "======================================"
echo ""
echo "Python SDK 发布:"
echo "  ./scripts/publish-python.sh dry-run   # 干运行测试"
echo "  ./scripts/publish-python.sh test      # 发布到 Test PyPI"
echo "  ./scripts/publish-python.sh prod      # 发布到 PyPI"
echo ""
echo "TypeScript SDK 发布:"
echo "  ./scripts/publish-typescript.sh dry-run   # 干运行测试"
echo "  ./scripts/publish-typescript.sh prod      # 发布到 npm"
echo ""

log_info "配置完成!"
