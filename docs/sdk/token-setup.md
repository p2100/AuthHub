# Token 配置指南

## PyPI Token 安全配置

### ⚠️ 安全提醒

**绝对不要将 PyPI token 提交到 git 仓库！**

### 方法 1: 使用本地脚本（推荐用于临时使用）

1. **复制模板文件**
   ```bash
   cp scripts/pypi-token.sh.example scripts/pypi-token.sh
   ```

2. **编辑 `scripts/pypi-token.sh`，填入真实 token**
   ```bash
   vim scripts/pypi-token.sh
   # 或
   code scripts/pypi-token.sh
   ```

3. **使用时加载环境变量**
   ```bash
   source scripts/pypi-token.sh
   ```

4. **验证环境变量**
   ```bash
   echo $UV_PUBLISH_TOKEN
   ```

### 方法 2: 添加到 Shell 配置文件（推荐用于长期使用）

#### Bash 用户

编辑 `~/.bashrc` 或 `~/.bash_profile`：

```bash
echo "export UV_PUBLISH_TOKEN='pypi-AgEIcHlwaS5vcmcCJ...'" >> ~/.bashrc
source ~/.bashrc
```

#### Zsh 用户

编辑 `~/.zshrc`：

```bash
echo "export UV_PUBLISH_TOKEN='pypi-AgEIcHlwaS5vcmcCJ...'" >> ~/.zshrc
source ~/.zshrc
```

#### Fish 用户

```bash
set -Ux UV_PUBLISH_TOKEN 'pypi-AgEIcHlwaS5vcmcCJ...'
```

### 方法 3: 使用环境变量管理工具

#### direnv（推荐）

1. **安装 direnv**
   ```bash
   brew install direnv  # macOS
   # 或
   apt install direnv   # Linux
   ```

2. **创建 `.envrc` 文件**（已在 .gitignore 中）
   ```bash
   echo "export UV_PUBLISH_TOKEN='your-token'" > .envrc
   direnv allow
   ```

3. **自动加载**
   每次进入项目目录时自动加载环境变量

### 方法 4: CI/CD 环境

#### GitHub Actions

在 GitHub Repository Settings → Secrets and variables → Actions 中添加：

- Name: `UV_PUBLISH_TOKEN`
- Value: `pypi-AgEIcHlwaS5vcmcCJ...`

#### GitLab CI

在 GitLab Project Settings → CI/CD → Variables 中添加：

- Key: `UV_PUBLISH_TOKEN`
- Value: `pypi-AgEIcHlwaS5vcmcCJ...`
- Protected: ✅
- Masked: ✅

## 验证配置

运行发布脚本测试：

```bash
# Python SDK
cd sdk/python
bash ../../scripts/publish-python.sh

# TypeScript SDK
cd sdk/typescript
bash ../../scripts/publish-typescript.sh
```

## 如果 Token 泄露了

1. **立即撤销**：登录 PyPI → Account settings → API tokens → Revoke
2. **生成新 token**：创建新的 API token
3. **更新配置**：用新 token 替换所有地方的旧 token
4. **检查 git 历史**：如果已提交，需要清理 git 历史：
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch scripts/pypi-token.sh" \
     --prune-empty --tag-name-filter cat -- --all
   ```

## 最佳实践

1. ✅ 使用 `.gitignore` 忽略敏感文件
2. ✅ 使用环境变量而不是硬编码
3. ✅ 定期轮换 token
4. ✅ 为不同环境使用不同的 token
5. ✅ 使用最小权限原则（只授予必要的权限）

