#!/usr/bin/env python3
"""
自动更新版本号脚本

用法:
    python scripts/version_bump.py patch   # 1.0.0 -> 1.0.1
    python scripts/version_bump.py minor   # 1.0.0 -> 1.1.0
    python scripts/version_bump.py major   # 1.0.0 -> 2.0.0
"""

import json
import re
import sys
from pathlib import Path


def parse_version(version: str) -> tuple:
    """解析版本号"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"无效的版本号格式: {version}")
    return tuple(map(int, match.groups()))


def bump_version(version: str, bump_type: str) -> str:
    """升级版本号"""
    major, minor, patch = parse_version(version)

    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"无效的升级类型: {bump_type}。使用 'major', 'minor' 或 'patch'")


def update_manifest(new_version: str):
    """更新 prefab-manifest.json"""
    manifest_path = Path('prefab-manifest.json')

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    old_version = manifest['version']
    manifest['version'] = new_version

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"✅ 更新 prefab-manifest.json: {old_version} -> {new_version}")
    return old_version


def update_pyproject(new_version: str):
    """更新 pyproject.toml"""
    pyproject_path = Path('pyproject.toml')

    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则替换版本号
    pattern = r'(version\s*=\s*)"([^"]+)"'
    match = re.search(pattern, content)

    if match:
        old_version = match.group(2)
        new_content = re.sub(pattern, f'\\1"{new_version}"', content)

        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ 更新 pyproject.toml: {old_version} -> {new_version}")
    else:
        print("⚠️  pyproject.toml 中未找到版本号")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python scripts/version_bump.py [major|minor|patch]")
        print()
        print("示例:")
        print("  python scripts/version_bump.py patch   # 1.0.0 -> 1.0.1")
        print("  python scripts/version_bump.py minor   # 1.0.0 -> 1.1.0")
        print("  python scripts/version_bump.py major   # 1.0.0 -> 2.0.0")
        sys.exit(1)

    bump_type = sys.argv[1].lower()

    if bump_type not in ['major', 'minor', 'patch']:
        print(f"❌ 错误: 无效的升级类型 '{bump_type}'")
        print("   请使用 'major', 'minor' 或 'patch'")
        sys.exit(1)

    try:
        # 读取当前版本
        manifest_path = Path('prefab-manifest.json')
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        current_version = manifest['version']
        new_version = bump_version(current_version, bump_type)

        print(f"\n🔄 版本升级: {current_version} -> {new_version} ({bump_type})\n")

        # 更新文件
        update_manifest(new_version)
        update_pyproject(new_version)

        print(f"\n✅ 版本号已更新为 {new_version}")
        print(f"\n下一步:")
        print(f"  1. git add .")
        print(f"  2. git commit -m 'Bump version to {new_version}'")
        print(f"  3. git tag v{new_version}")
        print(f"  4. git push origin v{new_version}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
