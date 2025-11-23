"""
Gemini 图像生成预制件测试

测试所有暴露给 AI 的函数，确保它们按预期工作。
"""

import base64
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.main import edit_image, text_to_image


class TestTextToImage:
    """测试文本生成图像功能"""

    @patch('src.main.requests.post')
    def test_text_to_image_success(self, mock_post, monkeypatch):
        """测试成功生成图像"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)
        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        try:
            monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

            mock_response = MagicMock()
            mock_response.status_code = 200
            fake_image_data = base64.b64encode(b"fake_image_content").decode('utf-8')
            mock_response.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "inlineData": {
                                "data": fake_image_data
                            }
                        }]
                    }
                }]
            }
            mock_post.return_value = mock_response

            result = text_to_image(prompt="一只可爱的猫咪")

            assert result["success"] is True
            assert result["prompt"] == "一只可爱的猫咪"
            assert result["message"] == "图像生成成功"

            output_file = workspace_path / "data" / "outputs" / "generated_image.png"
            assert output_file.exists()
            assert output_file.read_bytes() == b"fake_image_content"

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir)

    def test_text_to_image_missing_api_key(self, monkeypatch):
        """测试缺少 API Key"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = text_to_image(prompt="测试提示词")

        assert result["success"] is False
        assert result["error_code"] == "MISSING_API_KEY"

    def test_text_to_image_invalid_prompt(self, monkeypatch):
        """测试无效的提示词"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        result = text_to_image(prompt="")

        assert result["success"] is False
        assert result["error_code"] == "INVALID_PROMPT"

    @patch('src.main.requests.post')
    def test_text_to_image_api_error(self, mock_post, monkeypatch):
        """测试 API 请求失败"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        result = text_to_image(prompt="测试提示词")

        assert result["success"] is False
        assert result["error_code"] == "API_REQUEST_FAILED"

    @patch('src.main.requests.post')
    def test_text_to_image_no_image_data(self, mock_post, monkeypatch):
        """测试 API 响应中没有图像数据"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"candidates": []}
        mock_post.return_value = mock_response

        result = text_to_image(prompt="测试提示词")

        assert result["success"] is False
        assert result["error_code"] == "NO_IMAGE_DATA"


class TestEditImage:
    """测试图像编辑功能"""

    @pytest.fixture
    def workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)

        inputs_dir = workspace_path / "data" / "inputs" / "input_image"
        inputs_dir.mkdir(parents=True)

        test_image = inputs_dir / "test.png"
        test_image.write_bytes(b"fake_input_image_content")

        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        yield workspace_path

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    @patch('src.main.requests.post')
    def test_edit_image_success(self, mock_post, workspace, monkeypatch):
        """测试成功编辑图像"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        fake_image_data = base64.b64encode(b"edited_image_content").decode('utf-8')
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "inlineData": {
                            "data": fake_image_data
                        }
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = edit_image(prompt="把背景改成蓝色")

        assert result["success"] is True
        assert result["prompt"] == "把背景改成蓝色"
        assert result["message"] == "图像编辑成功"

        output_file = workspace / "data" / "outputs" / "edited_image.png"
        assert output_file.exists()
        assert output_file.read_bytes() == b"edited_image_content"

    def test_edit_image_missing_api_key(self, workspace, monkeypatch):
        """测试缺少 API Key"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = edit_image(prompt="测试编辑")

        assert result["success"] is False
        assert result["error_code"] == "MISSING_API_KEY"

    def test_edit_image_invalid_prompt(self, workspace, monkeypatch):
        """测试无效的提示词"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        result = edit_image(prompt="")

        assert result["success"] is False
        assert result["error_code"] == "INVALID_PROMPT"

    def test_edit_image_no_input_file(self, workspace, monkeypatch):
        """测试没有输入文件"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        for f in (workspace / "data" / "inputs" / "input_image").glob("*"):
            f.unlink()

        result = edit_image(prompt="测试编辑")

        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    @patch('src.main.requests.post')
    def test_edit_image_api_error(self, mock_post, workspace, monkeypatch):
        """测试 API 请求失败"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = edit_image(prompt="测试编辑")

        assert result["success"] is False
        assert result["error_code"] == "API_REQUEST_FAILED"

    @patch('src.main.requests.post')
    def test_edit_image_with_jpeg(self, mock_post, monkeypatch):
        """测试支持 JPEG 格式"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)
        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        try:
            inputs_dir = workspace_path / "data" / "inputs" / "input_image"
            inputs_dir.mkdir(parents=True)
            test_image = inputs_dir / "test.jpg"
            test_image.write_bytes(b"fake_jpeg_content")

            monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

            mock_response = MagicMock()
            mock_response.status_code = 200
            fake_image_data = base64.b64encode(b"edited_jpeg_content").decode('utf-8')
            mock_response.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "inlineData": {
                                "data": fake_image_data
                            }
                        }]
                    }
                }]
            }
            mock_post.return_value = mock_response

            result = edit_image(prompt="测试编辑")

            assert result["success"] is True

            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            assert request_data['contents'][0]['parts'][1]['inline_data']['mime_type'] == 'image/jpeg'

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir)
