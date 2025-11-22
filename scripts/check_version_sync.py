#!/usr/bin/env python3
"""
版本同步检查脚本

检查 prefab-manifest.json 和 pyproject.toml 中的版本号是否一致
"""

import json
import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli
    except ImportError:
        print("⚠️  警告: 无法导入 tomli/tomllib，跳过版本检查")
        sys.exit(0)


def main():
    """检查版本号是否同步"""
    root = Path(__file__).parent.parent
    manifest_path = root / "prefab-manifest.json"
    pyproject_path = root / "pyproject.toml"

    # 读取 manifest 版本
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            manifest_version = manifest.get("version")
    except Exception as e:
        print(f"❌ 读取 prefab-manifest.json 失败: {e}")
        sys.exit(1)

    # 读取 pyproject.toml 版本
    try:
        with open(pyproject_path, 'rb') as f:
            pyproject = tomli.load(f)
            pyproject_version = pyproject.get("project", {}).get("version")
    except Exception as e:
        print(f"❌ 读取 pyproject.toml 失败: {e}")
        sys.exit(1)

    # 检查版本是否一致
    if not manifest_version:
        print("❌ prefab-manifest.json 中未找到 version 字段")
        sys.exit(1)

    if not pyproject_version:
        print("❌ pyproject.toml 中未找到 project.version 字段")
        sys.exit(1)

    if manifest_version != pyproject_version:
        print("❌ 版本号不一致!")
        print(f"   prefab-manifest.json: {manifest_version}")
        print(f"   pyproject.toml:       {pyproject_version}")
        print()
        print("💡 请确保两个文件中的版本号相同，或使用 scripts/version_bump.py 脚本统一更新版本")
        sys.exit(1)

    print(f"✅ 版本号一致: {manifest_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
