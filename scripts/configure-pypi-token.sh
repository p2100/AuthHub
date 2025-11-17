#!/bin/bash

# PyPI Token 配置脚本
# 使用方法: ./scripts/configure-pypi-token.sh

echo "===== PyPI Token 配置 ====="
echo ""
echo "步骤说明:"
echo "1. 访问 https://pypi.org/manage/account/token/"
echo "2. 点击 'Add API token'"
echo "3. Token name: 'authhub-sdk-publish-token'"
echo "4. Scope: 'Entire account (all projects)'"
echo "5. 复制生成的完整 token (格式: pypi-xxxxxxxxxxxxxx)"
echo ""

read -p "请粘贴你的 PyPI token: " token

if [[ -z "$token" ]]; then
    echo "错误: token 不能为空"
    exit 1
fi

# 确保 token 格式正确
if [[ ! "$token" =~ ^pypi- ]]; then
    echo "错误: token 应该以 'pypi-' 开头"
    echo "请确保复制的是完整的 token，包含 'pypi-' 前缀"
    exit 1
fi

# 设置环境变量
export UV_PUBLISH_TOKEN="$token"

# 保存到配置文件
CONFIG_FILE="$HOME/.authhub-pypi-token"
echo "export UV_PUBLISH_TOKEN='$token'" > "$CONFIG_FILE"

echo ""
echo "✓ Token 已配置成功!"
echo "✓ 当前会话已生效"
echo "✓ 配置文件已保存: $CONFIG_FILE"
echo ""
echo "永久生效方法:"
echo "  echo 'source $CONFIG_FILE' >> ~/.zshrc"
echo ""
echo "手动设置方法:"
echo "  export UV_PUBLISH_TOKEN='$token'"
echo ""
echo "现在可以重新运行发布脚本:"
echo "  ./scripts/publish-python.sh prod"
