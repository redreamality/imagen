"""
Gemini 图像生成工具 (NanoBanana2)

本预制件使用 Google Gemini API 实现图像生成和编辑功能。

功能：
1. text_to_image: 根据文本提示词生成图像
2. edit_image: 基于现有图片进行编辑

📁 文件路径约定（重要！）：
- 输入文件路径：data/inputs/{files.key}/
  例如：manifest 中 files.input_image → data/inputs/input_image/
- 输出文件：data/outputs/
- Gateway 自动下载文件到 inputs，自动上传 outputs 中的文件

API 端点: https://gemini.visualize.top/v1beta/models/gemini-3-pro-image-preview:generateContent
模型: gemini-3-pro-image-preview
"""

import base64
import os
from pathlib import Path

import requests

# 固定路径常量
DATA_OUTPUTS = Path("data/outputs")
DATA_INPUTS_IMAGE = Path("data/inputs/input_image")

# API 配置
GEMINI_API_URL = "https://gemini.visualize.top/v1beta/models/gemini-3-pro-image-preview:generateContent"


def text_to_image(prompt: str) -> dict:
    """
    根据文本提示词生成图像

    使用 Gemini API 根据用户提供的文本描述生成图像。
    生成的图像会自动保存到输出目录，由平台自动上传。

    Args:
        prompt: 图像生成提示词，描述想要生成的图像内容

    Returns:
        包含生成结果的字典，包含以下字段：
            - success: 操作是否成功
            - prompt: 使用的提示词（成功时）
            - message: 操作消息（成功时）
            - error: 错误信息（失败时）
            - error_code: 错误代码（失败时）

    Examples:
        >>> text_to_image(prompt="一只可爱的猫咪坐在窗边")
        {'success': True, 'prompt': '一只可爱的猫咪坐在窗边', 'message': '图像生成成功'}
    """
    try:
        api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            return {
                "success": False,
                "error": "未配置 GEMINI_API_KEY，请在平台上配置该密钥",
                "error_code": "MISSING_API_KEY"
            }

        if not prompt or not isinstance(prompt, str):
            return {
                "success": False,
                "error": "prompt 参数必须是非空字符串",
                "error_code": "INVALID_PROMPT"
            }

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API 请求失败: {response.status_code} - {response.text}",
                "error_code": "API_REQUEST_FAILED"
            }

        result = response.json()

        if "candidates" not in result or not result["candidates"]:
            return {
                "success": False,
                "error": "API 响应中没有生成的图像数据",
                "error_code": "NO_IMAGE_DATA"
            }

        image_data = result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        image_bytes = base64.b64decode(image_data)

        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        output_filename = "generated_image.png"
        output_path = DATA_OUTPUTS / output_filename
        output_path.write_bytes(image_bytes)

        return {
            "success": True,
            "prompt": prompt,
            "message": "图像生成成功"
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "API 请求超时，请稍后重试",
            "error_code": "REQUEST_TIMEOUT"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"网络请求错误: {str(e)}",
            "error_code": "NETWORK_ERROR"
        }
    except KeyError as e:
        return {
            "success": False,
            "error": f"API 响应格式错误: {str(e)}",
            "error_code": "INVALID_RESPONSE_FORMAT"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def edit_image(prompt: str) -> dict:
    """
    基于现有图片进行编辑

    使用 Gemini API 根据用户提供的编辑指令，对输入图像进行修改。
    输入图像从 data/inputs/input_image/ 目录自动读取（由平台自动下载）。
    编辑后的图像会保存到输出目录，由平台自动上传。

    Args:
        prompt: 图像编辑指令，描述想要对图像进行的修改

    Returns:
        包含编辑结果的字典，包含以下字段：
            - success: 操作是否成功
            - prompt: 使用的编辑指令（成功时）
            - message: 操作消息（成功时）
            - error: 错误信息（失败时）
            - error_code: 错误代码（失败时）

    Examples:
        >>> edit_image(prompt="把背景改成蓝天白云")
        {'success': True, 'prompt': '把背景改成蓝天白云', 'message': '图像编辑成功'}
    """
    try:
        api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            return {
                "success": False,
                "error": "未配置 GEMINI_API_KEY，请在平台上配置该密钥",
                "error_code": "MISSING_API_KEY"
            }

        if not prompt or not isinstance(prompt, str):
            return {
                "success": False,
                "error": "prompt 参数必须是非空字符串",
                "error_code": "INVALID_PROMPT"
            }

        input_files = list(DATA_INPUTS_IMAGE.glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入图像文件",
                "error_code": "NO_INPUT_FILE"
            }

        input_path = input_files[0]

        if not input_path.is_file():
            return {
                "success": False,
                "error": "输入路径不是有效的文件",
                "error_code": "INVALID_INPUT_FILE"
            }

        input_image_bytes = input_path.read_bytes()
        input_image_base64 = base64.b64encode(input_image_bytes).decode('utf-8')

        suffix = input_path.suffix.lower()
        mime_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_type_map.get(suffix, 'image/png')

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        data = {
            "contents": [{
                "parts": [
                    {"text": f"基于这张图片，生成一个新版本：{prompt}"},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": input_image_base64
                        }
                    }
                ]
            }]
        }

        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=90)

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API 请求失败: {response.status_code} - {response.text}",
                "error_code": "API_REQUEST_FAILED"
            }

        result = response.json()

        if "candidates" not in result or not result["candidates"]:
            return {
                "success": False,
                "error": "API 响应中没有生成的图像数据",
                "error_code": "NO_IMAGE_DATA"
            }

        image_data = result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        image_bytes = base64.b64decode(image_data)

        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        output_filename = "edited_image.png"
        output_path = DATA_OUTPUTS / output_filename
        output_path.write_bytes(image_bytes)

        return {
            "success": True,
            "prompt": prompt,
            "message": "图像编辑成功"
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "API 请求超时，请稍后重试",
            "error_code": "REQUEST_TIMEOUT"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"网络请求错误: {str(e)}",
            "error_code": "NETWORK_ERROR"
        }
    except KeyError as e:
        return {
            "success": False,
            "error": f"API 响应格式错误: {str(e)}",
            "error_code": "INVALID_RESPONSE_FORMAT"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
