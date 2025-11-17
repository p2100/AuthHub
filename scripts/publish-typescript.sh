#!/bin/bash
set -e

# AuthHub TypeScript SDK 发布脚本
# 使用方法: ./publish-typescript.sh [dry-run|prod]

SDK_PATH="/Users/leo/code/work/AuthHub/sdk/typescript"
ENVIRONMENT=${1:-"dry-run"}

echo "===== AuthHub TypeScript SDK 发布工具 ====="
echo "环境: $ENVIRONMENT"
echo "SDK路径: $SDK_PATH"
echo "=========================================="

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

CURRENT_VERSION=$(grep '"version"' package.json | cut -d'"' -f4)
log_info "当前版本: v$CURRENT_VERSION"

# 2. 检查是否需要更新版本
read -p "是否需要更新版本号?(y/n): " update_version
if [[ "$update_version" == "y" ]]; then
    echo "请选择版本更新类型:"
    echo "1) patch (0.1.0 -> 0.1.1)"
    echo "2) minor (0.1.0 -> 0.2.0)"
    echo "3) major (0.1.0 -> 1.0.0)"
    echo "4) prerelease (0.1.0 -> 0.1.1-alpha.0)"
    echo "5) 自定义"
    read -p "选择(1-5): " version_type

    case $version_type in
        1)
            pnpm version patch --no-git-tag-version
            ;;
        2)
            pnpm version minor --no-git-tag-version
            ;;
        3)
            pnpm version major --no-git-tag-version
            ;;
        4)
            pnpm version prerelease --preid=alpha --no-git-tag-version
            ;;
        5)
            read -p "请输入新版本号: " custom_version
            pnpm version "$custom_version" --no-git-tag-version
            ;;
        *)
            log_warn "使用当前版本"
            ;;
    esac

    NEW_VERSION=$(grep '"version"' package.json | cut -d'"' -f4)
    log_info "新版本: v$NEW_VERSION"
fi

# 3. 安装依赖
log_info "安装依赖..."
pnpm install

# 4. 运行 lint
log_info "运行代码检查..."
pnpm lint || log_warn "Lint 警告, 请检查"

# 5. 运行测试
log_info "运行测试..."
pnpm test || log_warn "测试失败, 请检查"

# 6. 构建包
log_info "构建包..."
rm -rf dist/
pnpm build

# 7. 显示构建结果
echo ""
echo "构建文件:"
ls -lh dist/
echo ""

# 8. 确认发布
if [[ "$ENVIRONMENT" == "dry-run" ]]; then
    log_info "干运行模式, 仅构建不发布"

    # 显示 npm 信息
    echo ""
    echo "包信息预览:"
    npm pack --dry-run

    exit 0
fi

read -p "确认发布到 npm? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    log_warn "发布取消"
    exit 0
fi

# 9. 验证 npm 登录
log_info "验证 npm 登录状态..."
if ! npm whoami &> /dev/null; then
    log_error "未登录 npm"
    echo "请运行: pnpm login"
    exit 1
fi

log_info "当前用户: $(npm whoami)"

# 10. 发布
if [[ "$ENVIRONMENT" == "prod" ]]; then
    log_info "发布到 npm..."

    # 检查是否是 scoped package
    PACKAGE_NAME=$(grep '"name"' package.json | cut -d'"' -f4)
    if [[ "$PACKAGE_NAME" == @* ]]; then
        pnpm publish --access public
    else
        pnpm publish
    fi
else
    log_error "未知环境: $ENVIRONMENT"
    echo "使用方法: $0 [dry-run|prod]"
    exit 1
fi

log_info "发布成功!"
log_info "请访问: https://www.npmjs.com/package/$PACKAGE_NAME"
