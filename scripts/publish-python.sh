#!/bin/bash
set -e

# AuthHub Python SDK 发布脚本
# 使用方法: ./publish-python.sh [test|prod]

SDK_PATH="/Users/leo/code/work/AuthHub/sdk/python"
ENVIRONMENT=${1:-"dry-run"}
export UV_PUBLISH_TOKEN='pypi-AgEIcHlwaS5vcmcCJDIyMDdjOTNmLTNmY2EtNGZhMy04ZDBmLThlYzhmYjliZTUxMwACKlszLCI3NDZkZjMwMC03YTM3LTRkYjAtYTEzOS03MmJhMDYzMjI2ZWIiXQAABiBAelChUnOtzEiheozu6VXm_W6KMSmmrzXJBoFqJo65Ng'
echo "===== AuthHub Python SDK 发布工具 ====="
echo "环境: $ENVIRONMENT"
echo "SDK路径: $SDK_PATH"
echo "======================================"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 检查当前版本
cd "$SDK_PATH"

CURRENT_VERSION=$(grep -E '^version\s*=' pyproject.toml | cut -d'=' -f2 | sed 's/[" ]//g')
log_info "当前版本: v$CURRENT_VERSION"

# 2. 检查是否需要更新版本
read -p "是否需要更新版本号?(y/n): " update_version
if [[ "$update_version" == "y" ]]; then
    echo "请选择版本更新类型:"
    echo "1) patch (0.1.0 -> 0.1.1)"
    echo "2) minor (0.1.0 -> 0.2.0)"
    echo "3) major (0.1.0 -> 1.0.0)"
    echo "4) 自定义"
    read -p "选择(1-4): " version_type

    case $version_type in
        1)
            # patch: 0.1.0 -> 0.1.1
            log_info "执行: uv version --bump patch"
            uv version --bump patch --no-sync
            ;;
        2)
            # minor: 0.1.0 -> 0.2.0
            log_info "执行: uv version --bump minor"
            uv version --bump minor --no-sync
            ;;
        3)
            # major: 0.1.0 -> 1.0.0
            log_info "执行: uv version --bump major"
            uv version --bump major --no-sync
            ;;
        4)
            read -p "请输入新版本号: " NEW_VERSION
            log_info "执行: uv version $NEW_VERSION"
            uv version "$NEW_VERSION" --no-sync
            ;;
        *)
            log_warn "使用当前版本"
            ;;
    esac

    NEW_VERSION=$(grep -E '^version\s*=' pyproject.toml | cut -d'=' -f2 | sed 's/[" ]//g')
    log_info "版本已更新: $CURRENT_VERSION -> $NEW_VERSION"
fi

# 3. 运行测试
log_info "运行测试..."
if command -v pytest &> /dev/null; then
    pytest tests/ || log_warn "测试失败，请检查"
else
    log_warn "pytest 未安装，跳过测试"
fi

# 4. 构建包
log_info "构建包..."
rm -rf dist/

# 使用 --no-sources 确保包可以独立构建（推荐用于发布）
log_info "执行: uv build --no-sources"
uv build --no-sources

# 5. 显示构建结果
echo ""
echo "构建文件:"
ls -lh dist/
echo ""

# 6. 确认发布
if [[ "$ENVIRONMENT" == "dry-run" ]]; then
    log_info "干运行模式, 仅构建不发布"
    log_info "构建文件位于: $SDK_PATH/dist/"
    exit 0
fi

read -p "确认发布到 $ENVIRONMENT? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    log_warn "发布取消"
    exit 0
fi

# 7. 发布
if [[ "$ENVIRONMENT" == "test" ]]; then
    log_info "发布到 Test PyPI..."
    
    # 检查 Test PyPI token
    if [[ -z "$UV_PUBLISH_TOKEN" ]]; then
        log_error "未设置 UV_PUBLISH_TOKEN 环境变量"
        echo "请设置: export UV_PUBLISH_TOKEN='pypi-your-test-token'"
        echo "获取 token: https://test.pypi.org/manage/account/token/"
        exit 1
    fi
    
    log_info "执行: uv publish --publish-url https://test.pypi.org/legacy/"
    uv publish --publish-url https://test.pypi.org/legacy/
    
    log_info "发布成功!"
    log_info "请访问: https://test.pypi.org/project/authhub-sdk/"
    
elif [[ "$ENVIRONMENT" == "prod" ]]; then
    log_info "发布到生产 PyPI..."

    # 检查 PyPI token
    if [[ -z "$UV_PUBLISH_TOKEN" ]]; then
        log_error "未设置 UV_PUBLISH_TOKEN 环境变量"
        echo "请设置: export UV_PUBLISH_TOKEN='pypi-your-prod-token'"
        echo "获取 token: https://pypi.org/manage/account/token/"
        exit 1
    fi

    log_info "执行: uv publish"
    uv publish
    
    log_info "发布成功!"
    log_info "请访问: https://pypi.org/project/authhub-sdk/"
    
else
    log_error "未知环境: $ENVIRONMENT"
    echo "使用方法: $0 [test|prod]"
    exit 1
fi
