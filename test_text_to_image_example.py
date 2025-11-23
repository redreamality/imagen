#!/usr/bin/env python3
"""
测试脚本：运行 text_to_image 函数并保存图片

由于没有实际的 GEMINI_API_KEY，此脚本使用 mock 来模拟 API 响应，
生成一个测试图片并保存到 data/outputs/ 目录。
"""

import base64
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.main import text_to_image


def create_test_image():
    """创建一个简单的测试图片（1x1 像素的 PNG）"""
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x05\x18\r\xa2d\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return png_data


def main():
    """运行 text_to_image 测试"""
    print("=" * 60)
    print("测试 text_to_image 函数")
    print("=" * 60)
    
    os.environ['GEMINI_API_KEY'] = 'test-api-key-for-demo'
    
    test_image_data = create_test_image()
    base64_image = base64.b64encode(test_image_data).decode('utf-8')
    
    with patch('src.main.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "inlineData": {
                            "data": base64_image
                        }
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        prompt = "一只可爱的橙色猫咪坐在窗边看着日落"
        print(f"\n📝 提示词: {prompt}")
        print("\n🔄 调用 text_to_image 函数...")
        
        result = text_to_image(prompt=prompt)
        
        print(f"\n✅ 结果:")
        print(f"   - success: {result.get('success')}")
        print(f"   - message: {result.get('message')}")
        print(f"   - prompt: {result.get('prompt')}")
        
        if result.get('success'):
            output_file = Path("data/outputs/generated_image.png")
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"\n📁 文件已保存:")
                print(f"   - 路径: {output_file.absolute()}")
                print(f"   - 大小: {file_size} bytes")
                print(f"\n✨ 测试成功！图片已保存到 {output_file}")
            else:
                print(f"\n❌ 错误: 文件未找到 {output_file}")
        else:
            print(f"\n❌ 错误:")
            print(f"   - error: {result.get('error')}")
            print(f"   - error_code: {result.get('error_code')}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
