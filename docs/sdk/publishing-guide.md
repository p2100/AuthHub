# SDK 发布指南

本指南说明如何发布 AuthHub SDK 到 PyPI 和 npm。

## 📦 Python SDK 发布

### 前置要求

1. **安装 uv**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **获取 PyPI Token**
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - 生产 PyPI: https://pypi.org/manage/account/token/

3. **设置环境变量**
   ```bash
   # Test PyPI
   export UV_PUBLISH_TOKEN="pypi-your-test-token"
   
   # 生产 PyPI
   export UV_PUBLISH_TOKEN="pypi-your-prod-token"
   ```

### 发布步骤

#### 1. 测试发布（推荐先测试）

```bash
./scripts/publish-python.sh test
```

流程：
1. 选择版本更新类型（patch/minor/major）
2. 运行测试
3. 构建包（使用 `uv build --no-sources`）
4. 确认发布
5. 发布到 Test PyPI

验证：
```bash
# 从 Test PyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ authhub-sdk
```

#### 2. 生产发布

```bash
./scripts/publish-python.sh prod
```

流程同上，但发布到生产 PyPI。

验证：
```bash
pip install authhub-sdk
```

### 版本更新策略

根据语义化版本（SemVer）选择更新类型：

| 类型 | 说明 | 示例 |
|------|------|------|
| **patch** | 向后兼容的 bug 修复 | 0.1.0 → 0.1.1 |
| **minor** | 向后兼容的新功能 | 0.1.0 → 0.2.0 |
| **major** | 不向后兼容的变更 | 0.1.0 → 1.0.0 |

### 使用 uv version 命令

脚本内部使用的 uv 命令：

```bash
# 更新版本号
uv version --bump patch    # 0.1.0 → 0.1.1
uv version --bump minor    # 0.1.0 → 0.2.0
uv version --bump major    # 0.1.0 → 1.0.0
uv version 2.0.0          # 设置为指定版本

# 预览（不实际修改）
uv version --bump minor --dry-run

# 不触发 sync
uv version --bump minor --no-sync
```

### 构建选项

```bash
# 标准构建
uv build

# 发布构建（推荐）- 不使用 tool.uv.sources
uv build --no-sources

# 构建特定包
uv build --package <PACKAGE>
```

### 发布选项

```bash
# 发布到 PyPI
uv publish

# 发布到 Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# 使用 token
uv publish --token pypi-xxx

# 或设置环境变量
export UV_PUBLISH_TOKEN="pypi-xxx"
uv publish
```

### 故障排查

#### 问题 1: 版本已存在

```
HTTP error 400: File already exists
```

**解决**：更新版本号后重新发布。PyPI 不允许覆盖已存在的版本。

#### 问题 2: Token 无效

```
HTTP error 403: Invalid or non-existent authentication information
```

**解决**：
1. 检查 token 是否正确
2. 确认 token 对应的 PyPI 环境（test vs prod）
3. 重新生成 token

#### 问题 3: 构建失败

```
error: Failed to build package
```

**解决**：
1. 检查 `pyproject.toml` 配置
2. 确保 `[build-system]` 已定义
3. 运行 `uv build --no-sources` 测试

#### 问题 4: 部分文件上传失败

使用 `--check-url` 选项避免重复上传：

```bash
uv publish --check-url https://pypi.org/simple/
```

---

## 📦 TypeScript SDK 发布

### 前置要求

1. **npm 账号**
   - 注册：https://www.npmjs.com/signup
   - 登录：`npm login`

2. **配置 .npmrc**
   ```bash
   # 设置 registry（可选）
   registry=https://registry.npmjs.org/
   ```

### 发布步骤

#### 1. 更新版本

```bash
cd sdk/typescript

# 使用 npm version 更新版本号
npm version patch   # 0.1.0 → 0.1.1
npm version minor   # 0.1.0 → 0.2.0
npm version major   # 0.1.0 → 1.0.0
```

#### 2. 构建

```bash
pnpm build
```

#### 3. 发布

```bash
# 测试发布（dry run）
npm publish --dry-run

# 正式发布
npm publish
```

或使用脚本：

```bash
./scripts/publish-typescript.sh prod
```

### npm 发布配置

在 `package.json` 中：

```json
{
  "name": "@chenjing194/authhub-sdk",
  "version": "0.1.0",
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "files": [
    "dist"
  ],
  "publishConfig": {
    "access": "public"
  }
}
```

### 验证发布

```bash
# 安装已发布的包
npm install @chenjing194/authhub-sdk

# 或使用 npx 测试
npx @chenjing194/authhub-sdk
```

---

## 🔐 安全建议

### Token 管理

1. **不要提交 token 到代码仓库**
   ```bash
   # .gitignore 中应包含
   .env
   .env.local
   *.token
   ```

2. **使用项目级别的 token**
   - 为每个项目创建独立的 token
   - 限制 token 权限范围

3. **定期轮换 token**
   - 建议每 90 天更换一次
   - 泄露后立即撤销

### CI/CD 发布

在 GitHub Actions 中使用 Trusted Publisher：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # 必需的，用于 Trusted Publisher
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Build
        run: uv build --no-sources
      - name: Publish
        run: uv publish
```

配置 Trusted Publisher：
1. 访问 PyPI 项目设置
2. 添加 GitHub Actions Trusted Publisher
3. 填写仓库信息

---

## 📋 发布检查清单

### 发布前

- [ ] 代码已提交并推送
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 版本号符合语义化版本规范
- [ ] 依赖版本已锁定

### 发布时

- [ ] 选择正确的环境（test/prod）
- [ ] 版本号更新正确
- [ ] 构建成功
- [ ] 发布成功

### 发布后

- [ ] 在 PyPI/npm 上验证包信息
- [ ] 测试安装和导入
- [ ] 更新文档中的版本号
- [ ] 创建 Git tag
- [ ] 发布 Release Notes

---

## 🔗 相关链接

### Python
- [uv 文档](https://docs.astral.sh/uv/)
- [PyPI 官网](https://pypi.org/)
- [Test PyPI](https://test.pypi.org/)
- [Python 打包指南](https://packaging.python.org/)

### TypeScript
- [npm 文档](https://docs.npmjs.com/)
- [npm Registry](https://www.npmjs.com/)
- [tsup 文档](https://tsup.egoist.dev/)

---

## 🤔 常见问题

### Q: 如何撤销已发布的版本？

**A**: PyPI 不支持删除已发布的版本，但可以 "yank"（标记为不推荐）：

```bash
# 需要使用 twine 或 PyPI 网页界面
pip install twine
twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing dist/*
```

### Q: 发布失败了怎么办？

**A**: 
1. 检查错误信息
2. 验证 token 和权限
3. 确认版本号未被使用
4. 查看构建日志
5. 使用 `--dry-run` 测试

### Q: 如何发布 alpha/beta 版本？

**A**:
```bash
# Python
uv version --bump minor --bump alpha  # 0.1.0 → 0.2.0a1
uv version --bump beta                # 0.2.0a1 → 0.2.0b1

# TypeScript
npm version prerelease --preid=alpha  # 0.1.0 → 0.1.1-alpha.0
npm version prerelease --preid=beta   # 0.1.1-alpha.0 → 0.1.1-beta.0
```

---

**最后更新**: 2025-11-17  
**维护者**: AuthHub Team

