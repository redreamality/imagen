#!/usr/bin/env python3
"""
验证 prefab-manifest.json 与 src/main.py 的一致性

此脚本检查：
1. manifest.json 中声明的所有函数在 main.py 中都存在
2. 函数参数的数量和名称匹配
3. manifest.json 的格式正确
4. 类型系统规范
5. secrets 字段规范
"""

import ast
import json
import re
import sys
from pathlib import Path

# 类型系统定义
VALID_TYPES = {
    # 基础类型（JSON Schema）
    'string',
    'number',
    'integer',
    'boolean',
    'object',
    'array',
    # 平台感知类型
    'InputFile',
    'OutputFile'
}

# secrets 名称格式（大写字母、数字和下划线）
SECRET_NAME_PATTERN = re.compile(r'^[A-Z0-9_]+$')


def validate_files_definition(func_name, files_def):
    """
    验证 files 字段定义

    files 格式：
    {
      "input": {...},
      "output": {...},
      "watermark": {...}  // 支持多个命名文件组
    }
    """
    errors = []

    if not isinstance(files_def, dict):
        errors.append(f"函数 '{func_name}': files 字段必须是对象")
        return errors

    # 验证每个文件组
    for file_key, file_spec in files_def.items():
        # 检查必需字段
        if 'type' not in file_spec:
            errors.append(f"函数 '{func_name}': files.{file_key} 缺少 'type' 字段")
            continue

        # files 必须是 array 类型
        if file_spec['type'] != 'array':
            errors.append(f"函数 '{func_name}': files.{file_key}.type 必须是 'array'")
            continue

        # 检查 items 定义
        if 'items' not in file_spec:
            errors.append(f"函数 '{func_name}': files.{file_key} 缺少 'items' 字段")
            continue

        items = file_spec['items']
        if 'type' not in items:
            errors.append(f"函数 '{func_name}': files.{file_key}.items 缺少 'type' 字段")
        elif items['type'] not in ('InputFile', 'OutputFile'):
            errors.append(f"函数 '{func_name}': files.{file_key}.items.type 必须是 'InputFile' 或 'OutputFile'，当前是 '{items['type']}'")

        # 检查 InputFile 的必需字段
        if items.get('type') == 'InputFile':
            if 'minItems' not in file_spec:
                errors.append(f"函数 '{func_name}': files.{file_key} 应定义 'minItems'")
            if 'maxItems' not in file_spec:
                errors.append(f"函数 '{func_name}': files.{file_key} 应定义 'maxItems'")

    return errors


def load_manifest():
    """加载并解析 manifest 文件"""
    manifest_path = Path("prefab-manifest.json")
    if not manifest_path.exists():
        print("❌ 错误: prefab-manifest.json 文件不存在")
        return None

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        return manifest
    except json.JSONDecodeError as e:
        print(f"❌ 错误: prefab-manifest.json 格式不正确: {e}")
        return None


def extract_function_signatures(main_py_path):
    """从 main.py 提取函数签名"""
    if not main_py_path.exists():
        print(f"❌ 错误: {main_py_path} 文件不存在")
        return None

    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except SyntaxError as e:
        print(f"❌ 错误: {main_py_path} 语法错误: {e}")
        return None

    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 只提取模块级别的函数（不在类内部）
            # 检查函数是否在类定义内部
            is_in_class = False
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    parent_body = getattr(parent, 'body', [])
                    # 确保 body 是列表类型再检查
                    if isinstance(parent_body, list) and node in parent_body:
                        is_in_class = True
                        break

            # 只处理不在类中的函数，且不是以 _ 开头的私有函数
            if not is_in_class and not node.name.startswith('_'):
                params = []
                defaults_start = len(node.args.args) - len(node.args.defaults)

                for i, arg in enumerate(node.args.args):
                    param_info = {
                        'name': arg.arg,
                        'required': i < defaults_start
                    }
                    params.append(param_info)

                functions[node.name] = params

    return functions


def validate_manifest_schema(manifest):
    """验证 manifest 的基本模式"""
    required_fields = ['schema_version', 'id', 'version', 'entry_point', 'dependencies_file', 'functions']

    for field in required_fields:
        if field not in manifest:
            print(f"❌ 错误: manifest 缺少必需字段: {field}")
            return False

    if manifest['entry_point'] != 'src/main.py':
        print(f"❌ 错误: entry_point 必须是 'src/main.py', 当前值: {manifest['entry_point']}")
        return False

    if manifest['dependencies_file'] != 'pyproject.toml':
        print(f"❌ 错误: dependencies_file 必须是 'pyproject.toml', 当前值: {manifest['dependencies_file']}")
        return False

    return True


def validate_type_recursive(obj, path=""):
    """递归验证对象中所有的 type 字段是否符合类型系统规范"""
    errors = []

    if isinstance(obj, dict):
        # 检查当前对象的 type 字段
        if 'type' in obj:
            type_value = obj['type']
            if type_value not in VALID_TYPES:
                errors.append(f"{path}: 无效的类型 '{type_value}'，必须是以下之一: {', '.join(sorted(VALID_TYPES))}")

        # 递归检查子对象
        if 'properties' in obj and isinstance(obj['properties'], dict):
            for prop_name, prop_value in obj['properties'].items():
                errors.extend(validate_type_recursive(prop_value, f"{path}.properties.{prop_name}"))

        # 检查其他可能包含类型定义的字段
        for key in ['returns', 'items']:
            if key in obj:
                errors.extend(validate_type_recursive(obj[key], f"{path}.{key}"))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(validate_type_recursive(item, f"{path}[{i}]"))

    return errors


def validate_type_system(manifest):
    """验证 manifest 中的类型系统规范"""
    errors = []

    for func in manifest.get('functions', []):
        func_name = func.get('name', 'unknown')

        # 验证参数类型
        for param in func.get('parameters', []):
            param_name = param.get('name', 'unknown')
            param_errors = validate_type_recursive(param, f"函数 '{func_name}' 的参数 '{param_name}'")
            errors.extend(param_errors)

        # 验证返回值类型
        if 'returns' in func:
            return_errors = validate_type_recursive(func['returns'], f"函数 '{func_name}' 的返回值")
            errors.extend(return_errors)

    return errors


def validate_secrets(manifest):
    """验证 manifest 中的 secrets 字段规范"""
    errors = []
    warnings = []

    for func in manifest.get('functions', []):
        func_name = func.get('name', 'unknown')
        secrets = func.get('secrets', [])

        if not isinstance(secrets, list):
            errors.append(f"函数 '{func_name}': secrets 必须是数组类型")
            continue

        for i, secret in enumerate(secrets):
            if not isinstance(secret, dict):
                errors.append(f"函数 '{func_name}': secrets[{i}] 必须是对象类型")
                continue

            # 验证 name 字段
            if 'name' not in secret:
                errors.append(f"函数 '{func_name}': secrets[{i}] 缺少必需的 'name' 字段")
            else:
                secret_name = secret['name']
                if not isinstance(secret_name, str):
                    errors.append(f"函数 '{func_name}': secret 的 'name' 必须是字符串类型")
                elif not SECRET_NAME_PATTERN.match(secret_name):
                    errors.append(
                        f"函数 '{func_name}': secret 名称 '{secret_name}' 不符合规范，"
                        f"必须只包含大写字母、数字和下划线 (例如: API_KEY, DATABASE_URL)"
                    )

            # 验证 description 字段
            if 'description' not in secret:
                errors.append(f"函数 '{func_name}': secrets[{i}] 缺少必需的 'description' 字段")
            elif not isinstance(secret.get('description'), str):
                errors.append(f"函数 '{func_name}': secret 的 'description' 必须是字符串类型")

            # 验证 required 字段
            if 'required' not in secret:
                errors.append(f"函数 '{func_name}': secrets[{i}] 缺少必需的 'required' 字段")
            elif not isinstance(secret.get('required'), bool):
                errors.append(f"函数 '{func_name}': secret 的 'required' 必须是布尔类型")

            # 检查 instructions 字段（可选但推荐）
            if 'instructions' not in secret:
                warnings.append(
                    f"函数 '{func_name}': secret '{secret.get('name', 'unknown')}' 建议添加 'instructions' 字段，"
                    f"帮助用户了解如何获取该密钥"
                )
            elif secret.get('instructions') and not isinstance(secret['instructions'], str):
                errors.append(f"函数 '{func_name}': secret 的 'instructions' 必须是字符串类型")

    return errors, warnings


def validate_functions(manifest, actual_functions):
    """验证函数定义的一致性"""
    errors = []
    warnings = []

    manifest_functions = {f['name']: f for f in manifest['functions']}

    # 检查 manifest 中的函数是否都在 main.py 中存在
    for func_name, func_def in manifest_functions.items():
        if func_name not in actual_functions:
            errors.append(f"函数 '{func_name}' 在 manifest 中声明但在 main.py 中不存在")
            continue

        # 验证 files 字段（如果存在）
        if 'files' in func_def:
            file_errors = validate_files_definition(func_name, func_def['files'])
            errors.extend(file_errors)

        # 验证参数（files 中的参数不应该在函数签名中）
        manifest_params = {p['name']: p for p in func_def.get('parameters', [])}
        actual_params = {p['name']: p for p in actual_functions[func_name]}

        # 检查必需参数
        for param_name, param_info in manifest_params.items():
            if param_name not in actual_params:
                errors.append(f"函数 '{func_name}': 参数 '{param_name}' 在 manifest 中声明但在实际函数中不存在")
            elif param_info.get('required', False) and not actual_params[param_name]['required']:
                warnings.append(f"函数 '{func_name}': 参数 '{param_name}' 在 manifest 中标记为必需，但在函数中有默认值")

        # 检查实际参数是否都在 manifest 中
        for param_name, param_info in actual_params.items():
            if param_name not in manifest_params:
                warnings.append(f"函数 '{func_name}': 参数 '{param_name}' 在函数中存在但未在 manifest 中声明")

        # 验证返回值定义
        if 'returns' not in func_def:
            errors.append(f"函数 '{func_name}': 缺少 'returns' 字段定义")
        else:
            returns = func_def['returns']

            # 检查必需的字段
            if 'type' not in returns:
                errors.append(f"函数 '{func_name}': returns 缺少 'type' 字段")

            if 'description' not in returns:
                warnings.append(f"函数 '{func_name}': returns 缺少 'description' 字段")

            # 如果是 object 类型，建议定义 properties
            if returns.get('type') == 'object':
                if 'properties' not in returns:
                    warnings.append(f"函数 '{func_name}': returns 是 object 类型，建议定义 'properties' 以详细描述结构")
                else:
                    # 检查 properties 中的每个字段是否有 type 和 description
                    for prop_name, prop_def in returns['properties'].items():
                        if 'type' not in prop_def:
                            warnings.append(f"函数 '{func_name}': returns.properties.{prop_name} 缺少 'type' 字段")
                        if 'description' not in prop_def:
                            warnings.append(f"函数 '{func_name}': returns.properties.{prop_name} 缺少 'description' 字段")

    # 检查 main.py 中是否有未声明的公共函数
    for func_name in actual_functions:
        if not func_name.startswith('_') and func_name not in manifest_functions:
            warnings.append(f"函数 '{func_name}' 在 main.py 中定义但未在 manifest 中声明")

    return errors, warnings


def main():
    """主验证流程"""
    print("🔍 开始验证 prefab-manifest.json 与 src/main.py 的一致性...\n")

    # 加载 manifest
    manifest = load_manifest()
    if not manifest:
        sys.exit(1)

    # 验证 manifest 模式
    if not validate_manifest_schema(manifest):
        sys.exit(1)

    print("✅ Manifest 基本模式验证通过")

    # 验证类型系统
    type_errors = validate_type_system(manifest)
    if type_errors:
        print("\n❌ 类型系统验证失败:")
        for error in type_errors:
            print(f"  - {error}")
        print("\n请使用类型系统规范中定义的类型。")
        print(f"支持的类型: {', '.join(sorted(VALID_TYPES))}")
        sys.exit(1)

    print("✅ 类型系统验证通过")

    # 验证 secrets 字段
    secret_errors, secret_warnings = validate_secrets(manifest)
    if secret_errors:
        print("\n❌ Secrets 验证失败:")
        for error in secret_errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✅ Secrets 字段验证通过")

    # 提取实际函数签名
    main_py_path = Path("src/main.py")
    actual_functions = extract_function_signatures(main_py_path)
    if actual_functions is None:
        sys.exit(1)

    print(f"✅ 成功解析 main.py，发现 {len(actual_functions)} 个函数")

    # 验证函数一致性
    func_errors, func_warnings = validate_functions(manifest, actual_functions)

    # 合并所有警告
    all_warnings = secret_warnings + func_warnings

    # 输出结果
    if all_warnings:
        print("\n⚠️  警告:")
        for warning in all_warnings:
            print(f"  - {warning}")

    if func_errors:
        print("\n❌ 错误:")
        for error in func_errors:
            print(f"  - {error}")
        print("\n验证失败! 请修复上述错误。")
        sys.exit(1)

    print("\n✅ 验证成功! Manifest 与 main.py 完全一致。")
    sys.exit(0)


if __name__ == "__main__":
    main()
