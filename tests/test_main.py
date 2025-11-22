"""
预制件核心函数测试

测试所有暴露给 AI 的函数，确保它们按预期工作。
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.main import add_numbers, echo, fetch_weather, greet, process_text_file


class TestBasicFunctions:
    """测试基础函数"""

    def test_greet_default(self):
        """测试默认问候"""
        result = greet()
        assert result["success"] is True
        assert result["message"] == "Hello, World!"
        assert result["name"] == "World"

    def test_greet_with_name(self):
        """测试指定名字的问候"""
        result = greet(name="Alice")
        assert result["success"] is True
        assert result["message"] == "Hello, Alice!"
        assert result["name"] == "Alice"

    def test_greet_invalid(self):
        """测试无效输入"""
        result = greet(name="")
        assert result["success"] is False
        assert "error_code" in result

    def test_echo(self):
        """测试回显功能"""
        result = echo(text="Hello")
        assert result["success"] is True
        assert result["echo"] == "Hello"
        assert result["length"] == 5

    def test_echo_empty(self):
        """测试空文本"""
        result = echo(text="")
        assert result["success"] is False
        assert result["error_code"] == "EMPTY_TEXT"

    def test_add_numbers(self):
        """测试数字相加"""
        result = add_numbers(a=10, b=20)
        assert result["success"] is True
        assert result["sum"] == 30

    def test_add_numbers_negative(self):
        """测试负数"""
        result = add_numbers(a=-5, b=3)
        assert result["success"] is True
        assert result["sum"] == -2


class TestFileHandling:
    """测试文件处理功能"""

    @pytest.fixture
    def workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)

        # 创建目录结构（文件按 manifest key 组织）
        inputs_dir = workspace_path / "data" / "inputs" / "input"
        inputs_dir.mkdir(parents=True)

        # 创建测试输入文件
        test_file = inputs_dir / "test.txt"
        test_file.write_text("Hello World", encoding="utf-8")

        # 切换到工作空间
        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        yield workspace_path

        # 清理
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_process_text_file_uppercase(self, workspace):
        """测试文本转大写"""
        # 不传入文件参数
        result = process_text_file(operation="uppercase")

        assert result["success"] is True
        assert result["operation"] == "uppercase"
        assert result["original_length"] == 11
        assert result["processed_length"] == 11

        # 返回值不包含文件路径
        assert "input_file" not in result
        assert "output_file" not in result

        # 验证输出文件存在
        output_files = list((workspace / "data/outputs").glob("*"))
        assert len(output_files) == 1
        assert output_files[0].read_text(encoding="utf-8") == "HELLO WORLD"

    def test_process_text_file_lowercase(self, workspace):
        """测试文本转小写"""
        result = process_text_file(operation="lowercase")

        assert result["success"] is True
        assert result["operation"] == "lowercase"

        output_files = list((workspace / "data/outputs").glob("*"))
        assert len(output_files) == 1
        assert output_files[0].read_text(encoding="utf-8") == "hello world"

    def test_process_text_file_reverse(self, workspace):
        """测试文本反转"""
        result = process_text_file(operation="reverse")

        assert result["success"] is True
        assert result["operation"] == "reverse"

        output_files = list((workspace / "data/outputs").glob("*"))
        assert len(output_files) == 1
        assert output_files[0].read_text(encoding="utf-8") == "dlroW olleH"

    def test_process_text_file_no_input(self, workspace):
        """测试没有输入文件"""
        # 删除所有输入文件
        for f in (workspace / "data" / "inputs" / "input").glob("*"):
            f.unlink()

        result = process_text_file(operation="uppercase")

        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    def test_process_text_file_invalid_operation(self, workspace):
        """测试无效操作"""
        result = process_text_file(operation="invalid")

        assert result["success"] is False
        assert result["error_code"] == "INVALID_OPERATION"


class TestSecretsHandling:
    """测试密钥处理"""

    def test_fetch_weather_success(self, monkeypatch):
        """测试正常调用（有 API Key）"""
        # 设置环境变量
        monkeypatch.setenv("WEATHER_API_KEY", "test-api-key")

        result = fetch_weather(city="北京")

        assert result["success"] is True
        assert result["city"] == "北京"
        assert "temperature" in result
        assert "condition" in result

    def test_fetch_weather_missing_key(self, monkeypatch):
        """测试缺少 API Key"""
        # 确保环境变量不存在
        monkeypatch.delenv("WEATHER_API_KEY", raising=False)

        result = fetch_weather(city="北京")

        assert result["success"] is False
        assert result["error_code"] == "MISSING_API_KEY"

    def test_fetch_weather_invalid_city(self, monkeypatch):
        """测试无效城市"""
        monkeypatch.setenv("WEATHER_API_KEY", "test-api-key")

        result = fetch_weather(city="")

        assert result["success"] is False
        assert result["error_code"] == "INVALID_CITY"
