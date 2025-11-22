# AI Agents 开发指南

> 本文档为 AI 编程助手（如 Cursor、GitHub Copilot、Claude 等）提供项目上下文和开发指南。

## 项目概述

这是一个 **AI 预制件模板仓库**，用于创建可被 AI 直接调用的标准化 Python 代码模块。

### 核心目标
- 提供标准化的项目结构和配置
- 自动化测试、验证、打包和发布流程
- 降低社区贡献者的技术门槛
- 确保所有预制件的质量和一致性

## 技术栈

- **语言**: Python 3.11+
- **包管理**: uv (现代化的 Python 包管理器)
- **测试**: pytest
- **代码检查**: flake8, isort
- **Git Hooks**: pre-commit (自动代码质量检查)
- **构建**: setuptools
- **CI/CD**: GitHub Actions
- **配置**: pyproject.toml (PEP 621) + prefab-manifest.json

## 项目结构

```
prefab-template/
├── src/                          # 源代码目录
│   ├── __init__.py              # 模块导出
│   ├── main.py                  # 主入口（必须）
│   └── utils/                   # 工具模块示例
│       ├── __init__.py
│       └── math_utils.py
├── tests/                       # 测试目录
│   ├── test_main.py
│   └── test_utils.py
├── scripts/                     # 辅助脚本
│   ├── validate_manifest.py    # Manifest 验证
│   ├── version_bump.py         # 版本升级
│   └── quick_start.py          # 快速验证脚本
├── .github/workflows/           # GitHub Actions
│   └── build-and-release.yml   # 自动发布流程
├── prefab-manifest.json         # 函数元数据（核心）
├── pyproject.toml              # 项目配置
└── README.md                   # 文档
```

## 关键约定

### 1. 入口文件（不可更改）
- **必须**: `src/main.py` 是唯一的入口文件
- 所有暴露给 AI 的函数都必须在此定义
- 可以从其他模块导入辅助函数

### 2. 元数据文件（必须同步）
- `prefab-manifest.json` 必须与 `src/main.py` 保持一致
- 每个函数的签名、参数、返回值都必须准确描述
- 使用 **JSON Schema 类型**（`string`, `number`, `integer`, `boolean`, `object`, `array`）
- 支持平台感知类型：`InputFile`（输入文件）和 `OutputFile`（输出文件）
- 支持 **secrets 字段**：用于声明函数所需的密钥
- 版本号必须与 `pyproject.toml` 保持一致
- 运行 `uv run python scripts/validate_manifest.py` 验证一致性

### 3. 文件路径约定（重要！）

**路径规则**：
- 输入文件路径 = `data/inputs/{files.key}/`
- 输出文件路径 = `data/outputs/`

**实例**：
```python
# 如果 prefab-manifest.json 中定义：
{
  "files": {
    "input": { "type": "InputFile", ... }  // key 是 "input"
  }
}

# 则代码中应该使用：
DATA_INPUTS = Path("data/inputs/input")  # 注意是 /input/，不是 /inputs/
DATA_OUTPUTS = Path("data/outputs")

# 扫描输入文件：
input_files = list(DATA_INPUTS.glob("*"))
```

**常见错误**：
```python
# ❌ 错误：缺少 key
DATA_INPUTS = Path("data/inputs")  # 这会导致找不到文件！

# ✅ 正确：包含 prefab-manifest.json 中的 key
DATA_INPUTS = Path("data/inputs/input")  # 如果 files.input
DATA_INPUTS = Path("data/inputs/video")  # 如果 files.video
```

### 4. 依赖管理
```toml
[project]
dependencies = [
    # 运行时依赖（会被打包）
]

[project.optional-dependencies]
dev = [
    # 开发依赖（不会被打包）
]
```

### 5. 函数设计规范

#### 非流式函数（一次性返回）
```python
def function_name(param1: str, param2: int = 0) -> dict:
    """
    一句话描述函数功能

    Args:
        param1: 参数1说明
        param2: 参数2说明（可选）

    Returns:
        返回值说明
    """
    try:
        result = do_something()
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

#### 流式函数（实时返回）
```python
from typing import Iterator, Dict, Any

def stream_function(param: str) -> Iterator[Dict[str, Any]]:
    """
    一句话描述函数功能（流式）

    Args:
        param: 参数说明

    Yields:
        dict: SSE 事件数据
            - type: "start" | "progress" | "done" | "error"
            - data: 事件数据
    """
    try:
        # 发送开始事件
        yield {"type": "start", "data": {...}}

        # 处理并逐步返回
        for item in process_items():
            yield {"type": "progress", "data": item}

        # 发送完成事件
        yield {"type": "done", "data": {...}}

    except Exception as e:
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "ERROR_CODE"
        }
```

### 6. Secrets 管理规范

如果函数需要使用 API Key、数据库连接等敏感信息：

**在 prefab-manifest.json 中声明：**
```json
{
  "functions": [{
    "name": "fetch_weather",
    "secrets": [
      {
        "name": "WEATHER_API_KEY",
        "description": "天气服务 API 密钥",
        "instructions": "请访问 https://api.weather.com/keys 获取",
        "required": true
      }
    ]
  }]
}
```

**在代码中使用：**
```python
import os

def fetch_weather(city: str) -> dict:
    # 从环境变量获取（平台自动注入）
    api_key = os.environ.get('WEATHER_API_KEY')

    if not api_key:
        return {
            "success": False,
            "error": "未配置 WEATHER_API_KEY",
            "error_code": "MISSING_API_KEY"
        }

    # 使用 API Key...
```

**Secrets 字段规范：**
- `name`: 必需，大写字母+数字+下划线（如 `API_KEY`）
- `description`: 必需，简短说明密钥用途
- `instructions`: 推荐，指导用户如何获取密钥
- `required`: 必需，布尔值，标识是否为必需

## 开发工作流

### 初始设置
```bash
# 1. 安装 uv
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 同步依赖
uv sync --dev

# 3. 安装 git hooks（推荐）
uv run pre-commit install

# 4. 运行验证
uv run python scripts/quick_start.py
```

### Pre-commit Hooks（代码质量保障）

**强烈推荐安装！** Pre-commit hooks 会在每次 `git commit` 前自动运行检查，避免提交有问题的代码。

安装后，每次提交时会自动检查：
- ✅ Flake8 代码风格（避免 F401 等错误）
- ✅ isort 导入排序
- ✅ Manifest 验证（与 main.py 一致性）
- ✅ 单元测试（确保所有测试通过）
- ✅ 版本同步（prefab-manifest.json 与 pyproject.toml 版本一致）

```bash
# 安装 hooks
uv run pre-commit install

# 手动运行所有检查
uv run pre-commit run --all-files
```

**示例：提交时自动检查**
```bash
$ git commit -m "feat: add new function"

# 自动运行检查...
flake8...................................................Passed
isort....................................................Passed
Validate prefab-manifest.json............................Passed
Run pytest...............................................Passed
Check version sync.......................................Passed

# ✅ 所有检查通过，提交成功！
```

### 日常开发
```bash
# 运行测试
uv run pytest tests/ -v

# 代码风格检查
uv run flake8 src/ --max-line-length=120

# 验证 manifest
uv run python scripts/validate_manifest.py
```

### 发布流程
```bash
# 1. 更新 prefab-manifest.json 和 pyproject.toml 中的 version（必须一致）
# 2. 提交代码
git add .
git commit -m "Release v1.0.0"

# 3. 创建并推送 tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions 会自动构建 .whl 包并发布
```

## AI 助手使用指南

### 编辑代码时
1. **始终保持一致性**: 修改 `main.py` 后必须同步更新 `prefab-manifest.json`
2. **遵循类型提示**: 所有函数参数和返回值都要有类型提示
3. **编写测试**: 每个函数都应该有对应的测试用例
4. **返回结构化数据**: 优先返回包含 `success` 字段的字典

### 添加新函数
1. 在 `src/main.py` 中定义函数
2. 在 `prefab-manifest.json` 中添加函数描述
3. 在 `tests/test_main.py` 中添加测试
4. 运行 `uv run python scripts/validate_manifest.py` 验证
5. 更新 `src/__init__.py` 导出列表

### 添加依赖
```bash
# 运行时依赖
uv add package-name

# 开发依赖
uv add --dev package-name
```

### 常见问题

**Q: 可以修改项目结构吗？**
A: `src/main.py` 和 `prefab-manifest.json` 的位置和作用不可更改，但可以在 `src/` 下添加更多模块。

**Q: 如何处理敏感信息？**
A: **推荐使用 secrets 功能**。在 `prefab-manifest.json` 中声明 `secrets` 字段，平台会自动引导用户配置并注入到环境变量。参见本文档的 "Secrets 管理规范" 章节和 `fetch_weather` 示例。

**Q: CI/CD 失败怎么办？**
A: 查看 GitHub Actions 日志，通常是测试失败或 manifest 不一致。本地运行验证脚本排查。

## 验证清单

在提交代码前，确保：
- [ ] 所有测试通过 (`uv run pytest tests/ -v`)
- [ ] 代码风格正确 (`uv run flake8 src/`)
- [ ] Manifest 验证通过 (`uv run python scripts/validate_manifest.py`)
- [ ] 文档已更新（README.md）
- [ ] 版本号一致（prefab-manifest.json 和 git tag）

## 自动化特性

### 自动触发的流程
- **推送 tag**: 自动构建、测试、打包、发布
- **版本验证**: 确保 tag 版本与 manifest 版本一致
- **依赖打包**: 自动下载并打包运行时依赖

### 构建产物（v2 格式）
- 格式: Python Wheel (`.whl`)
- 内容: `src/` + `prefab-manifest.json` + 运行时依赖
- 位置: GitHub Release 附件
- 优势: 标准 Python 包格式，更好的兼容性

## 最佳实践

1. **小步提交**: 每个功能点单独提交
2. **测试先行**: 先写测试，再写实现
3. **清晰命名**: 函数名应该是动词+名词形式
4. **错误处理**: 所有可能失败的地方都要捕获异常
5. **文档完善**: 保持 README 和代码注释同步更新

## 参考资源

- [项目文档](README.md) - 完整的使用指南
- [贡献指南](CONTRIBUTING.md) - 如何贡献代码
- [变更日志](CHANGELOG.md) - 版本更新记录

---

**提示**: 如果你是 AI 助手，在修改代码时请始终参考本文档的约定和规范。
