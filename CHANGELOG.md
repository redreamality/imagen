# 更新日志

本文档记录了预制件模板的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [3.0.0] - 2025-10-16

### 🎉 重大更新 - v3.0 架构正式确立

这是一个重要的架构升级版本，正式确立了 `pyproject.toml` + `prefab-manifest.json` 的双文件核心模式，并引入了完整的密钥管理规范。

### 新增

- 🔐 **密钥管理系统（Secrets）**
  - 在 `prefab-manifest.json` 中新增 `secrets` 字段支持
  - 完整的密钥声明规范：`name`, `description`, `instructions`, `required`
  - 密钥名称格式验证（大写字母、数字和下划线）
  - 平台会自动将用户配置的密钥注入到环境变量中

- 📝 **示例函数扩展**
  - 新增 `fetch_weather(city)` 函数，演示如何使用 secrets
  - 展示从环境变量读取密钥的最佳实践
  - 完整的错误处理和用户友好提示

- ✅ **增强的验证功能**
  - `validate_manifest.py` 支持 secrets 字段验证
  - 自动检查密钥名称格式是否符合规范
  - 验证必需字段的完整性
  - 提供 instructions 字段缺失警告

- 🧪 **测试覆盖**
  - 为 `fetch_weather` 函数添加完整的单元测试
  - 测试覆盖：有/无 API Key、无效城市名、多城市查询
  - 使用 pytest 的 `monkeypatch` 模拟环境变量

### 变更

- 🔧 **构建系统更新**
  - 从 `hatchling` 切换到 `setuptools` 作为构建后端
  - 更新 `pyproject.toml` 配置以符合 v3.0 规范
  - 优化 package-data 配置，确保 manifest.json 正确打包

- 📚 **文档全面更新**
  - README.md：新增"密钥管理"章节，包含完整示例和规范说明
  - AGENTS.md：添加"Secrets 管理规范"指南，更新技术栈信息
  - 更新常见问题解答，推荐使用 v3.0 的 secrets 功能

### 修复

- 🐛 修复 `validate_manifest.py` 中未使用的导入
- 🐛 修复代码缩进问题以符合 flake8 规范
- 🐛 添加文件末尾换行符

### 架构改进

- **双文件核心模式正式确立**
  - `pyproject.toml`：负责 Python 打包、依赖管理
  - `prefab-manifest.json`：负责定义预制件的"API 契约"和元数据
  - 两个文件各司其职，职责清晰

- **DevEx 优化**
  - 废弃 `prefab-devkit` 的概念
  - 回归纯粹、简单、无额外工具依赖的模板
  - 开发者只需关注标准 Python 工具

### 技术栈更新

- Python 3.11+ （不变）
- uv 包管理器 （不变）
- setuptools >= 61.0 （从 hatchling 切换）
- pytest 测试框架 （不变）
- flake8 代码检查 （不变）

### 升级指南

如果你正在使用旧版本的模板，请按以下步骤升级：

1. **更新 `pyproject.toml`**：
   ```toml
   [build-system]
   requires = ["setuptools>=61.0"]
   build-backend = "setuptools.build_meta"

   [tool.setuptools.packages.find]
   where = ["."]
   include = ["src*"]

   [tool.setuptools.package-data]
   "*" = ["*.json"]
   ```

2. **（可选）添加 secrets 支持**：
   - 在 `prefab-manifest.json` 的函数定义中添加 `secrets` 数组
   - 在代码中使用 `os.environ.get()` 读取环境变量
   - 参考 `fetch_weather` 函数示例

3. **更新验证脚本**：
   - 替换 `scripts/validate_manifest.py` 为新版本
   - 新版本支持 v3.0 的 secrets 字段验证

4. **运行验证**：
   ```bash
   uv run python scripts/validate_manifest.py
   uv run pytest tests/ -v
   ```

### 示例代码

**Manifest 中声明 secrets：**
```json
{
  "functions": [{
    "name": "fetch_weather",
    "secrets": [
      {
        "name": "WEATHER_API_KEY",
        "description": "用于认证天气服务的 API 密钥",
        "instructions": "请访问 https://api.weather.com/keys 获取",
        "required": true
      }
    ]
  }]
}
```

**代码中使用 secrets：**
```python
import os

def fetch_weather(city: str) -> dict:
    api_key = os.environ.get('WEATHER_API_KEY')
    if not api_key:
        return {
            "success": False,
            "error": "未配置 WEATHER_API_KEY",
            "error_code": "MISSING_API_KEY"
        }
    # 使用 API Key...
```

### 参考文档

- [PRD v3.0](prd%20v3.0.md) - 完整的产品需求文档
- [README.md](README.md) - 更新的用户指南
- [AGENTS.md](AGENTS.md) - AI 助手开发指南

---

## [1.0.0] - 2025-10-14

### 新增
- 🎉 初始版本发布
- ✨ 标准化的项目文件结构
- 🤖 完整的 CI/CD 自动化流程（GitHub Actions）
- 📦 自动打包和发布机制
- ✅ Manifest 验证脚本
- 🧪 完整的单元测试示例
- 📚 详细的文档和使用指南

### 核心功能
- `src/main.py` - 预制件核心代码入口
- `prefab-manifest.json` - AI 可理解的函数元数据
- `.github/workflows/build-and-release.yml` - 自动化 CI/CD
- `scripts/validate_manifest.py` - 一致性验证工具
- `scripts/quick_start.py` - 快速验证脚本

### 示例函数
- `analyze_dataset(data, operation)` - 数据集分析功能
  - 支持统计分析、求和、平均值计算
  - 完整的错误处理和类型定义
  - 展示结构化返回值的最佳实践

### 文档
- `README.md` - 完整的用户指南
- `CONTRIBUTING.md` - 贡献者指南
- `ARCHITECTURE.md` - 架构设计文档
- `QUICK_REFERENCE.md` - 快速参考卡片
- `DOCS_INDEX.md` - 文档导航索引
- `AGENTS.md` - AI 助手开发指南
- Issue 和 PR 模板

### 质量保证
- Pytest 单元测试框架
- Flake8 代码风格检查
- Manifest 自动验证
- 版本号一致性检查

---

## 版本规划

### [1.1.0] - 计划中
- [ ] 添加更多示例预制件
- [ ] 支持异步函数
- [ ] 添加性能测试工具
- [ ] 优化错误提示信息

### [2.0.0] - 未来展望
- [ ] 支持多语言（TypeScript, Go）
- [ ] 集成更多 CI/CD 平台（GitLab CI, Jenkins）
- [ ] 可视化配置工具

---

## 贡献者

感谢所有为此项目做出贡献的开发者！

如果您发现问题或有改进建议，欢迎：
- 提交 [Issue](https://github.com/your-org/prefab-template/issues)
- 发起 [Pull Request](https://github.com/your-org/prefab-template/pulls)
- 参与 [讨论](https://github.com/your-org/prefab-template/discussions)
