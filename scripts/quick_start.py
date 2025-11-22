#!/usr/bin/env python3
"""
快速开始脚本

运行此脚本来验证你的开发环境是否正确设置
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print(result.stdout[:500])  # 显示前500个字符
            return True
        else:
            print(f"❌ {description} - 失败")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except Exception as e:
        print(f"❌ {description} - 错误: {e}")
        return False


def check_python_version():
    """检查 Python 版本"""
    print_header("检查 Python 版本")

    version = sys.version_info
    print(f"当前 Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python 版本符合要求 (3.11+)")
        return True
    else:
        print("❌ Python 版本不符合要求，请使用 Python 3.11 或更高版本")
        return False


def check_files():
    """检查必需文件"""
    print_header("检查项目文件")

    required_files = [
        'src/main.py',
        'prefab-manifest.json',
        'pyproject.toml',
        'tests/test_main.py',
        '.github/workflows/build-and-release.yml',
        'scripts/validate_manifest.py'
    ]

    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            all_exist = False

    return all_exist


def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("  预制件模板 - 快速开始验证")
    print("🚀" * 30)

    results = []

    # 1. 检查 Python 版本
    results.append(check_python_version())

    # 2. 检查文件
    results.append(check_files())

    # 3. 安装依赖
    print_header("安装依赖")
    results.append(run_command(
        "uv sync --dev",
        "使用 uv 安装 Python 依赖"
    ))

    # 4. 运行测试
    print_header("运行测试")
    results.append(run_command(
        "uv run --with pytest pytest tests/ -v",
        "运行单元测试"
    ))

    # 5. 代码风格检查
    print_header("代码风格检查")
    results.append(run_command(
        "uv run --with flake8 flake8 src/ --max-line-length=120",
        "Flake8 代码风格检查"
    ))

    # 6. 验证 Manifest
    print_header("验证 Manifest")
    results.append(run_command(
        "uv run python scripts/validate_manifest.py",
        "Manifest 一致性验证"
    ))

    # 总结
    print_header("验证总结")

    if all(results):
        print("\n🎉 恭喜！所有检查都通过了！")
        print("\n你的开发环境已正确设置，可以开始开发了。")
        print("\n下一步:")
        print("  1. 修改 src/main.py 编写你的业务逻辑")
        print("  2. 更新 prefab-manifest.json 描述你的函数")
        print("  3. 在 tests/test_main.py 中添加测试")
        print("  4. 运行 'git tag v1.0.0 && git push origin v1.0.0' 发布")
        return 0
    else:
        print("\n⚠️  部分检查未通过，请查看上面的错误信息并修复。")
        print("\n常见问题:")
        print("  - 如果依赖安装失败，请检查网络连接")
        print("  - 如果测试失败，请查看具体的测试输出")
        print("  - 如果 Manifest 验证失败，请确保 JSON 格式正确")
        return 1


if __name__ == "__main__":
    sys.exit(main())
