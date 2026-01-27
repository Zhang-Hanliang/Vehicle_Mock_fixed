# GitHub Actions Workflow 对比分析

## 📋 文件对比

**文件 1（您的新版本）:**
- 路径: `Mock_Test/.github/workflows/build-ccu-vehicle-mock-single.yml`
- 特点: 简化版，通用 CI/CD 流程

**文件 2（原始版本）:**
- 路径: `swdv.enterer.minidemocar-main/.github/workflows/build-ccu-vehicle-mock-single.yml`
- 特点: 原始 CCU 项目的完整流程

---

## 🔍 详细对比

### **1. 基础配置对比**

| 项目 | Mock_Test (新) | minidemocar (原) | 说明 |
|-----|---------------|------------------|------|
| **运行环境** | `ubuntu-22.04` | `ubuntu-22.04` + `devcontainer` | 原版使用 velocitas 开发容器 |
| **权限** | read/write/checks | read/write/checks/deployments | 原版多了 deployments 权限 |
| **触发方式** | `workflow_call` | `workflow_call` | 两者相同 ✅ |

### **2. 步骤对比**

#### **共同步骤（两者都有）:**

```yaml
✅ Checkout repository
✅ Set up QEMU (多架构支持)
✅ Set up Docker Buildx
✅ Docker Login (GHCR)
✅ 准备 repository name (小写转换)
```

#### **Mock_Test (新版本) 特有步骤:**

```yaml
⭐ Prepare patched Dockerfile for CI
   - 动态创建 Dockerfile.ci
   - 修复 staticx 构建问题 (--no-build-isolation)
   - 修复 pyinstaller 隐藏导入问题
   - 避免直接修改仓库中的 Dockerfile
```

#### **minidemocar (原版本) 特有步骤:**

```yaml
⭐ Setup git credentials
   - 配置 GitHub Token 认证
   
⭐ Init velocitas project
   - 运行 velocitas init
   - 初始化 velocitas 项目环境
   
⭐ Setup git config
   - 配置 git 用户信息
   - 用于自动提交
```

---

## 🎯 关键差异分析

### **差异 1: 构建上下文路径**

**Mock_Test (新版本):**
```yaml
context: ./vehicle-mock
file: ./vehicle-mock/Dockerfile.ci
```
✅ **正确** - 适用于您的项目结构（vehicle-mock 在根目录）

**minidemocar (原版本):**
```yaml
context: ./CCU/vehicle-mock
file: ./CCU/vehicle-mock/Dockerfile
```
❌ **不适用** - 原项目的路径在 CCU 子目录下

---

### **差异 2: Dockerfile 处理策略**

**Mock_Test (新版本): 动态补丁策略**
```bash
# 优点：
✅ 不修改仓库中的 Dockerfile
✅ 仅在 CI 环境应用补丁
✅ 保持本地开发环境干净
✅ 灵活处理不同平台的构建问题

# 具体补丁：
1. staticx 修复: 添加 --no-build-isolation
   → 解决 arm64 平台 staticx wheel 构建失败
   
2. pyinstaller 修复: 添加 jaraco 隐藏导入
   → 避免 collect-submodules 引入非法模块名
```

**minidemocar (原版本): 直接使用原始 Dockerfile**
```yaml
file: ./CCU/vehicle-mock/Dockerfile

# 缺点：
❌ 需要在仓库中直接修改 Dockerfile
❌ 本地开发和 CI 使用相同配置
❌ 可能引入平台特定的补丁到主分支
```

---

### **差异 3: 镜像标签策略**

**Mock_Test (新版本): 动态标签**
```yaml
tags: |
  ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:dev
  ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:${{ github.sha }}
```
✅ **优点:**
- 自动使用仓库名称（zhang-hanliang/vehicle_mock_fixed）
- 提供开发标签 (`:dev`) 和提交标签 (`:sha`)
- 支持多版本并存

**minidemocar (原版本): 固定标签**
```yaml
tags: ghcr.io/bosch-engineering/swdv-enterer-minidemocar-ccu-vehicle-mock:v001arm
```
❌ **问题:**
- 硬编码组织名和仓库名
- 固定版本号 (v001arm)
- 不适合您的新仓库

---

### **差异 4: 平台支持**

**Mock_Test (新版本): 灵活的多平台支持**
```yaml
if [ "${{ inputs.platform }}" = "multiarch" ]; then
  echo "platforms=linux/amd64,linux/arm64"
else
  echo "platforms=linux/${{ inputs.platform }}"
fi
```
✅ **支持:**
- 单平台构建: `arm64` 或 `amd64`
- 多平台构建: `multiarch`（同时构建两个平台）

**minidemocar (原版本): 固定 arm64**
```yaml
platforms: "linux/arm64"
```
❌ **限制:**
- 只支持 arm64
- 不支持 amd64 或多平台

---

### **差异 5: Velocitas 集成**

**Mock_Test (新版本): 不依赖 Velocitas CLI**
```yaml
# 没有 velocitas init 步骤
# 不使用 velocitas 开发容器
# 直接使用 Docker 构建
```
✅ **优点:**
- 更快的构建速度（不需要初始化 velocitas 环境）
- 减少依赖（不需要 velocitas CLI）
- 更通用的 CI/CD 流程

**minidemocar (原版本): 深度集成 Velocitas**
```yaml
container: ghcr.io/eclipse-velocitas/devcontainer-base-images/python:v0.4

steps:
  - name: Init velocitas project
    run: velocitas init
```
❌ **问题:**
- 需要 velocitas 开发容器环境
- 构建时间更长
- 对于简单的 Docker 构建过于复杂

---

## ✅ 推荐的 Workflow 配置

基于您的项目结构和需求，**Mock_Test 的新版本更适合**，但需要一些调整：

### **建议的最终版本:**

```yaml
name: Build CCU vehicle-mock for single arch

on:
  workflow_call:
    inputs:
      platform:
        required: true
        type: string
      app_name:
        required: true
        type: string
  # 添加手动触发支持
  workflow_dispatch:
    inputs:
      platform:
        description: 'Target platform'
        required: true
        default: 'arm64'
        type: choice
        options:
          - arm64
          - amd64
          - multiarch

permissions:
  contents: read
  packages: write
  actions: write
  checks: write

jobs:
  build-image:
    name: "Building image (${{ inputs.app_name || 'vehicle-mock' }})"
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          submodules: "recursive"

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry (GHCR)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: repo_lc
        name: Prepare repository name in lower case
        uses: ASzc/change-string-case-action@v6
        with:
          string: ${{ github.repository }}

      - name: Set platform arguments
        id: set_args
        shell: bash
        run: |
          if [ "${{ inputs.platform }}" = "multiarch" ]; then
            echo "platforms=linux/amd64,linux/arm64" >> $GITHUB_OUTPUT
          else
            echo "platforms=linux/${{ inputs.platform }}" >> $GITHUB_OUTPUT
          fi

      # 关键步骤：动态生成 Dockerfile.ci
      - name: Prepare patched Dockerfile for CI
        shell: bash
        run: |
          cp vehicle-mock/Dockerfile vehicle-mock/Dockerfile.ci

          # 修复 staticx 构建问题 (arm64 平台)
          sed -i 's/pip3 install --no-cache-dir staticx/pip3 install --no-cache-dir --no-build-isolation staticx/g' vehicle-mock/Dockerfile.ci

          # 修复 pyinstaller 隐藏导入问题
          sed -i 's|^RUN pyinstaller --clean -F -s --paths=src mockprovider.py|RUN pyinstaller --clean -F -s --paths=src --hidden-import jaraco.text --hidden-import jaraco.functools --hidden-import jaraco.context mockprovider.py|g' vehicle-mock/Dockerfile.ci

          echo "=== Patched Dockerfile.ci ==="
          grep -n "staticx\|^RUN pyinstaller" vehicle-mock/Dockerfile.ci || true

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: ./vehicle-mock
          file: ./vehicle-mock/Dockerfile.ci
          push: true
          platforms: ${{ steps.set_args.outputs.platforms }}
          tags: |
            ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:latest
            ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:${{ github.sha }}
            ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:${{ inputs.platform }}
          labels: |
            org.opencontainers.image.source=https://github.com/${{ steps.repo_lc.outputs.lowercase }}
            org.opencontainers.image.revision=${{ github.sha }}
            org.opencontainers.image.created=${{ github.event.repository.updated_at }}

      - name: Print build summary
        run: |
          echo "✅ Build completed successfully!"
          echo ""
          echo "📦 Pushed images:"
          echo "  ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:latest"
          echo "  ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:${{ github.sha }}"
          echo "  ghcr.io/${{ steps.repo_lc.outputs.lowercase }}/vehicle-mock:${{ inputs.platform }}"
          echo ""
          echo "🏗️  Platform: ${{ steps.set_args.outputs.platforms }}"
```

---

## 🚀 使用建议

### **1. 主 Workflow 入口文件**

创建 `.github/workflows/build-vehicle-mock.yml`:

```yaml
name: Build Vehicle Mock

on:
  push:
    branches:
      - main
    paths:
      - 'vehicle-mock/**'
      - '.github/workflows/build-*.yml'
  pull_request:
    paths:
      - 'vehicle-mock/**'
  workflow_dispatch:
    inputs:
      platform:
        description: 'Target platform'
        required: true
        default: 'arm64'
        type: choice
        options:
          - arm64
          - amd64
          - multiarch

jobs:
  build-arm64:
    if: github.event_name != 'workflow_dispatch' || inputs.platform == 'arm64' || inputs.platform == 'multiarch'
    uses: ./.github/workflows/build-ccu-vehicle-mock-single.yml
    with:
      platform: arm64
      app_name: vehicle-mock

  build-amd64:
    if: github.event_name == 'workflow_dispatch' && (inputs.platform == 'amd64' || inputs.platform == 'multiarch')
    uses: ./.github/workflows/build-ccu-vehicle-mock-single.yml
    with:
      platform: amd64
      app_name: vehicle-mock

  build-multiarch:
    if: github.event_name == 'workflow_dispatch' && inputs.platform == 'multiarch'
    uses: ./.github/workflows/build-ccu-vehicle-mock-single.yml
    with:
      platform: multiarch
      app_name: vehicle-mock
```

### **2. 验证配置**

上传前验证：

```bash
# 1. 检查 workflow 语法
cd Mock_Test
gh workflow list

# 2. 本地测试 Docker 构建
cd vehicle-mock
docker build -t test-mock:local .

# 3. 验证修复后的 mock.py
grep -n "ExteriorLightControl" app/mock.py
# 应该看到第 16 行被注释
```

---

## 📊 总结对比表

| 特性 | Mock_Test (新) | minidemocar (原) | 推荐 |
|-----|---------------|------------------|------|
| **项目结构适配** | ✅ 适合新项目 | ❌ 原项目路径 | 新 |
| **构建策略** | ✅ 动态补丁 | ❌ 直接修改 | 新 |
| **镜像标签** | ✅ 动态灵活 | ❌ 硬编码 | 新 |
| **平台支持** | ✅ 多平台 | ❌ 仅 arm64 | 新 |
| **Velocitas 依赖** | ✅ 无依赖 | ❌ 强依赖 | 新 |
| **构建速度** | ✅ 快速 | ❌ 较慢 | 新 |
| **维护复杂度** | ✅ 简单 | ❌ 复杂 | 新 |

**结论：使用 Mock_Test 的新版本，无需修改！** ✅

---

## 🎯 下一步操作

```bash
# 1. 确认文件就绪
cd Mock_Test
ls -la .github/workflows/

# 2. 提交到 Git
git add .github/workflows/
git add vehicle-mock/app/mock.py
git add 最终系统架构与修复方案完整分析.md
git commit -m "feat: 修复灯光冲突问题，优化 CI/CD workflow"

# 3. 推送到 GitHub
git push origin main

# 4. 检查 GitHub Actions
# 访问: https://github.com/Zhang-Hanliang/Vehicle_Mock_fixed/actions
# 应该看到 workflow 自动触发
```

**您的 Mock_Test 版本已经是正确的配置，可以直接使用！** 🚀
