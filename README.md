# Gemini 图像生成工具 (NanoBanana2)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

使用 Google Gemini API 实现图像生成和编辑功能的 AI 预制件。

## 功能特性

### 1. 文本生成图像 (Text-to-Image)
根据文本提示词生成高质量图像。只需提供详细的文本描述，即可生成对应的图像。

### 2. 图像编辑 (Image Editing)
基于现有图像进行智能编辑。上传一张图片并提供编辑指令，AI 将根据你的要求修改图像。

## 技术栈

- **Python**: 3.11+
- **API**: Google Gemini API (gemini-3-pro-image-preview 模型)
- **依赖**: requests

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 2. 配置 API Key

在使用前，你需要获取 Google Gemini API Key：

1. 访问 [Google AI Studio](https://ai.google.dev/)
2. 注册并创建 API Key
3. 将 API Key 配置为环境变量 `GEMINI_API_KEY`

### 3. 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 查看测试覆盖率
uv run pytest tests/ --cov=src --cov-report=html
```

## 使用示例

### 文本生成图像

```python
from src.main import text_to_image

result = text_to_image(
    prompt="一只可爱的橘猫坐在窗台上，阳光洒在它身上，背景是蓝天白云"
)

if result["success"]:
    print("图像生成成功！")
    # 生成的图像保存在 data/outputs/generated_image.png
else:
    print(f"生成失败: {result['error']}")
```

### 图像编辑

```python
from src.main import edit_image

# 确保输入图像已放置在 data/inputs/input_image/ 目录下
result = edit_image(
    prompt="把背景改成蓝天白云，添加一只蝴蝶"
)

if result["success"]:
    print("图像编辑成功！")
    # 编辑后的图像保存在 data/outputs/edited_image.png
else:
    print(f"编辑失败: {result['error']}")
```

## 最佳实践

根据 Gemini 官方推荐，以下是生成高质量图像的技巧：

### 1. 具体化描述
提供详细的信息，而不是笼统的描述：
- ❌ "一套盔甲"
- ✅ "华丽的精灵板甲，蚀刻着银叶图案，带有高领和猎鹰翅膀形状的肩甲"

### 2. 提供上下文和意图
说明图片的用途，帮助模型更好地理解需求：
- ❌ "设计徽标"
- ✅ "为高端极简护肤品牌设计徽标"

### 3. 迭代和优化
利用对话特性进行多次调整：
- "这很棒，但你能让光线更暖一些吗？"
- "保持所有内容不变，但让角色的表情更严肃一些"

### 4. 使用分步指令
对于复杂场景，将提示拆分为多个步骤：
```
首先，创建一个宁静、薄雾弥漫的黎明森林的背景。
然后，在前景中添加一个长满苔藓的古老石制祭坛。
最后，将一把发光的剑放在祭坛顶部。
```

### 5. 控制镜头
使用摄影和电影术语控制构图：
- `wide-angle shot` (广角镜头)
- `macro shot` (微距镜头)
- `low-angle perspective` (低角度视角)

### 6. 图文生成
生成包含文字的图像时，先生成文字，再要求生成包含该文字的图片。

## API 说明

### text_to_image

根据文本提示词生成图像。

**参数:**
- `prompt` (string, 必需): 图像生成提示词

**返回:**
```json
{
  "success": true,
  "prompt": "提示词内容",
  "message": "图像生成成功"
}
```

### edit_image

基于现有图片进行编辑。

**参数:**
- `prompt` (string, 必需): 图像编辑指令

**输入文件:**
- 图像文件放置在 `data/inputs/input_image/` 目录
- 支持格式: PNG, JPEG, GIF, WebP

**返回:**
```json
{
  "success": true,
  "prompt": "编辑指令内容",
  "message": "图像编辑成功"
}
```

## 错误处理

所有函数都会返回结构化的错误信息：

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE"
}
```

常见错误代码：
- `MISSING_API_KEY`: 未配置 Gemini API Key
- `INVALID_PROMPT`: 提示词无效（为空或非字符串）
- `NO_INPUT_FILE`: 找不到输入文件（仅图像编辑）
- `API_REQUEST_FAILED`: API 请求失败
- `NO_IMAGE_DATA`: API 响应中没有图像数据
- `REQUEST_TIMEOUT`: 请求超时
- `NETWORK_ERROR`: 网络错误

## 文件路径约定

- **输入文件**: `data/inputs/{files.key}/`
  - 图像编辑: `data/inputs/input_image/`
- **输出文件**: `data/outputs/`
  - 平台会自动上传输出目录中的所有文件

## 开发指南

### 运行验证

```bash
# 验证 manifest 与代码一致性
uv run python scripts/validate_manifest.py

# 运行快速验证
uv run python scripts/quick_start.py
```

### 代码质量检查

```bash
# 代码风格检查
uv run flake8 src/ --max-line-length=120

# 导入排序检查
uv run isort src/ --check-only
```

### Pre-commit Hooks

推荐安装 pre-commit hooks 以确保代码质量：

```bash
uv run pre-commit install
```

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 相关资源

- [Google Gemini API 文档](https://ai.google.dev/gemini-api/docs)
- [Gemini 图像生成指南](https://ai.google.dev/gemini-api/docs/image-generation)
- [预制件开发指南](PREFAB_GUIDE.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

NanoBanana2

---

*Built with ❤️ using Google Gemini API*
