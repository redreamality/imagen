"""
预制件核心逻辑模块

这是一个示例预制件，展示了如何创建可被 AI 调用的函数。
所有暴露给 AI 的函数都必须在此文件中定义。

📁 文件路径约定（重要！）：
- 输入文件路径：data/inputs/{files.key}/
  例如：manifest 中 files.input → data/inputs/input/
  例如：manifest 中 files.video → data/inputs/video/
- 输出文件：data/outputs/
- Gateway 自动下载文件到 inputs，自动上传 outputs 中的文件

⚠️ 常见错误：
- ❌ 错误：DATA_INPUTS = Path("data/inputs")
- ✅ 正确：DATA_INPUTS = Path("data/inputs/input")  # 如果 manifest 中 key 是 "input"

📖 完整开发指南请查看：PREFAB_GUIDE.md

🌊 流式函数说明：
- 使用生成器函数（yield）实现流式返回
- 在 manifest 中设置 "streaming": true
- 适用于实时输出、进度报告、大数据处理等场景
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, Iterator

# 固定路径常量
# 文件组按 manifest 中的 key 组织（这里是 "input"）
# 如果你的 manifest 中使用不同的 key，请相应修改路径
# 例如：files.video → Path("data/inputs/video")
DATA_INPUTS = Path("data/inputs/input")
DATA_OUTPUTS = Path("data/outputs")


def greet(name: str = "World") -> dict:
    """
    向用户问候

    这是一个简单的示例函数，展示了预制件函数的基本结构。

    Args:
        name: 要问候的名字，默认为 "World"

    Returns:
        包含问候结果的字典

    Examples:
        >>> greet()
        {'success': True, 'message': 'Hello, World!', 'name': 'World'}

        >>> greet(name="Alice")
        {'success': True, 'message': 'Hello, Alice!', 'name': 'Alice'}
    """
    try:
        # 参数验证
        if not name or not isinstance(name, str):
            return {
                "success": False,
                "error": "name 参数必须是非空字符串",
                "error_code": "INVALID_NAME"
            }

        # 生成问候消息
        message = f"Hello, {name}!"

        return {
            "success": True,
            "message": message,
            "name": name
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def echo(text: str) -> dict:
    """
    回显输入的文本

    这个函数演示了基本的输入输出处理。

    Args:
        text: 要回显的文本

    Returns:
        包含回显结果的字典
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "text 参数不能为空",
                "error_code": "EMPTY_TEXT"
            }

        return {
            "success": True,
            "original": text,
            "echo": text,
            "length": len(text)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def add_numbers(a: float, b: float) -> dict:
    """
    计算两个数字的和

    这个函数演示了数值计算的基本模式。

    Args:
        a: 第一个数字
        b: 第二个数字

    Returns:
        包含计算结果的字典
    """
    try:
        result = a + b
        return {
            "success": True,
            "a": a,
            "b": b,
            "sum": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "CALCULATION_ERROR"
        }


def process_text_file(operation: str = "uppercase") -> dict:
    """
    处理文本文件（文件处理示例）

    这个函数演示了文件处理方式：
    - 文件不再作为参数传入
    - Gateway 自动下载到 data/inputs/
    - Prefab 自动扫描 data/inputs/
    - 输出写入 data/outputs/
    - Gateway 自动上传并在响应中返回文件 URL

    📁 文件约定：
    - 输入：自动扫描 data/inputs/（Gateway 已下载）
    - 输出：写入 data/outputs/（Gateway 会自动上传）
    - 返回值：不包含文件路径（由 Gateway 管理）

    Args:
        operation: 操作类型（uppercase, lowercase, reverse）

    Returns:
        包含处理结果的字典（不包含文件路径）
    """
    try:
        # 自动扫描 data/inputs 目录
        input_files = list(DATA_INPUTS.glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入文件",
                "error_code": "NO_INPUT_FILE"
            }

        # 获取第一个文件
        input_path = input_files[0]

        # 读取文件内容
        content = input_path.read_text(encoding="utf-8")

        # 执行操作
        if operation == "uppercase":
            result = content.upper()
        elif operation == "lowercase":
            result = content.lower()
        elif operation == "reverse":
            result = content[::-1]
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {operation}",
                "error_code": "INVALID_OPERATION"
            }

        # 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 写入输出文件（Gateway 会自动上传）
        output_filename = f"processed_{input_path.name}"
        output_path = DATA_OUTPUTS / output_filename
        output_path.write_text(result, encoding="utf-8")

        # 返回结果（不包含文件路径）
        return {
            "success": True,
            "operation": operation,
            "original_length": len(content),
            "processed_length": len(result)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def fetch_weather(city: str) -> dict:
    """
    获取指定城市的天气信息（示例函数，演示 secrets 的使用）

    这个函数演示了如何在预制件中使用密钥（secrets）。
    平台会自动将用户配置的密钥注入到环境变量中。

    注意：这是一个演示函数，实际不会调用真实的天气 API。

    Args:
        city: 要查询天气的城市名称

    Returns:
        包含天气信息的字典

    Examples:
        >>> fetch_weather(city="北京")
        {'success': True, 'city': '北京', 'temperature': 22.5, 'condition': '晴天'}
    """
    try:
        # 从环境变量中获取 API Key（平台会自动注入）
        api_key = os.environ.get('WEATHER_API_KEY')

        # 验证密钥是否已配置
        if not api_key:
            return {
                "success": False,
                "error": "未配置 WEATHER_API_KEY，请在平台上配置该密钥",
                "error_code": "MISSING_API_KEY"
            }

        # 验证参数
        if not city or not isinstance(city, str):
            return {
                "success": False,
                "error": "city 参数必须是非空字符串",
                "error_code": "INVALID_CITY"
            }

        # 这里是演示代码，实际应该调用真实的天气 API
        # import requests
        # response = requests.get(
        #     f"https://api.weather-provider.com/current",
        #     params={"city": city, "key": api_key}
        # )
        # data = response.json()

        # 演示：返回模拟数据
        return {
            "success": True,
            "city": city,
            "temperature": 22.5,
            "condition": "晴天",
            "note": "这是演示数据，未调用真实 API"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def count_stream(count: int = 10, interval: float = 0.5) -> Iterator[Dict[str, Any]]:
    """
    流式计数器（演示流式函数的实现）

    这是一个流式函数示例，展示如何使用生成器实现实时输出。
    适用于需要实时反馈的场景，如进度报告、实时数据处理等。

    🌊 流式函数特点：
    - 使用 Iterator[Dict] 作为返回类型
    - 使用 yield 逐步返回结果
    - 在 manifest 中设置 "streaming": true
    - 客户端通过 SSE (Server-Sent Events) 接收实时数据

    Args:
        count: 计数总数，默认 10
        interval: 每次计数的间隔秒数，默认 0.5

    Yields:
        dict: SSE 事件数据，包含以下字段：
            - type: 事件类型 ("start" | "progress" | "done" | "error")
            - data: 事件数据
            - metadata: 可选的元数据

    Examples:
        >>> for event in count_stream(count=5, interval=0.1):
        ...     print(event)
        {"type": "start", "data": {"total": 5}}
        {"type": "progress", "data": {"current": 1, "total": 5, "percentage": 20}}
        {"type": "progress", "data": {"current": 2, "total": 5, "percentage": 40}}
        ...
        {"type": "done", "data": {"total": 5, "completed": True}}
    """
    try:
        # 参数验证
        if count <= 0:
            yield {
                "type": "error",
                "data": "count 必须大于 0",
                "error_code": "INVALID_COUNT"
            }
            return

        if interval < 0:
            yield {
                "type": "error",
                "data": "interval 不能为负数",
                "error_code": "INVALID_INTERVAL"
            }
            return

        # Step 1: 发送开始事件
        yield {
            "type": "start",
            "data": {
                "total": count,
                "interval": interval
            }
        }

        # Step 2: 逐步计数并发送进度事件
        for i in range(1, count + 1):
            time.sleep(interval)

            percentage = int((i / count) * 100)

            yield {
                "type": "progress",
                "data": {
                    "current": i,
                    "total": count,
                    "percentage": percentage,
                    "message": f"正在计数: {i}/{count}"
                }
            }

        # Step 3: 发送完成事件
        yield {
            "type": "done",
            "data": {
                "total": count,
                "completed": True,
                "message": "计数完成"
            }
        }

    except Exception as e:
        # 发送错误事件
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
