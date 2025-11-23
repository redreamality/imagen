# How to Test the text_to_image Function

This guide explains how to test the `text_to_image` function for image generation.

## Quick Start

### 1. Install Dependencies

```bash
# Sync all dependencies including dev dependencies
uv sync --dev
```

### 2. Run the Test Script

```bash
# Run the test example
uv run python test_text_to_image_example.py
```

### 3. Verify the Output

The test will create:
- **Output file**: `data/outputs/generated_image.png`
- **Test results**: See `TEST_RESULTS.md` for detailed results

## What the Test Does

The `test_text_to_image_example.py` script:

1. ✅ Imports the `text_to_image` function from `src/main.py`
2. ✅ Mocks the Gemini API response (since we don't have a real API key)
3. ✅ Calls `text_to_image()` with a sample prompt
4. ✅ Generates and saves a test PNG image to `data/outputs/`
5. ✅ Validates the output file and reports results

## Understanding the Code

### Function Signature

```python
def text_to_image(prompt: str) -> dict:
    """
    根据文本提示词生成图像
    
    Args:
        prompt: 图像生成提示词
        
    Returns:
        dict: {
            "success": bool,
            "prompt": str,
            "message": str,
            "error": str (if failed),
            "error_code": str (if failed)
        }
    """
```

### Expected Workflow

```
User provides prompt
    ↓
Function checks GEMINI_API_KEY
    ↓
Validates prompt parameter
    ↓
Sends request to Gemini API
    ↓
Receives base64-encoded image
    ↓
Decodes and saves to data/outputs/
    ↓
Returns success response
```

## File Structure

```
project/
├── src/
│   └── main.py                        # Contains text_to_image function
├── data/
│   ├── inputs/                        # Input files directory
│   └── outputs/
│       └── generated_image.png        # Generated output (ignored by git)
├── test_text_to_image_example.py      # Test script
└── TEST_RESULTS.md                    # Test results documentation
```

## Testing with Real API

To test with a real Gemini API key:

1. Get your API key from https://ai.google.dev/

2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. Run the function without mocking:
   ```python
   from src.main import text_to_image
   
   result = text_to_image(prompt="a beautiful sunset over mountains")
   print(result)
   ```

4. Check the output:
   ```bash
   ls -lh data/outputs/generated_image.png
   ```

## Error Codes

The function may return these error codes:

| Error Code | Description |
|------------|-------------|
| `MISSING_API_KEY` | GEMINI_API_KEY not configured |
| `INVALID_PROMPT` | Prompt is empty or not a string |
| `API_REQUEST_FAILED` | API returned non-200 status |
| `NO_IMAGE_DATA` | API response missing image data |
| `REQUEST_TIMEOUT` | API request timed out |
| `NETWORK_ERROR` | Network connection issue |
| `INVALID_RESPONSE_FORMAT` | Unexpected API response format |
| `UNEXPECTED_ERROR` | Other unexpected errors |

## Running Unit Tests

To run the full test suite:

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src --cov-report=html

# Run only text_to_image tests
uv run pytest tests/test_main.py::TestTextToImage -v
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'requests'

**Solution**: Run `uv sync --dev` to install dependencies

### Issue: MISSING_API_KEY error

**Solution**: Either:
- Set `GEMINI_API_KEY` environment variable for real testing
- Use the provided test script which includes mocking

### Issue: Output directory not found

**Solution**: The function automatically creates `data/outputs/` directory

### Issue: Permission denied when saving file

**Solution**: Ensure you have write permissions in the project directory

## Example Output

When running the test script successfully:

```
============================================================
测试 text_to_image 函数
============================================================

📝 提示词: 一只可爱的橙色猫咪坐在窗边看着日落

🔄 调用 text_to_image 函数...

✅ 结果:
   - success: True
   - message: 图像生成成功
   - prompt: 一只可爱的橙色猫咪坐在窗边看着日落

📁 文件已保存:
   - 路径: /home/engine/project/data/outputs/generated_image.png
   - 大小: 68 bytes

✨ 测试成功！图片已保存到 data/outputs/generated_image.png

============================================================
```

## Next Steps

After successful testing:

1. ✅ Review `TEST_RESULTS.md` for detailed results
2. ✅ Check the generated image in `data/outputs/`
3. ✅ Try with different prompts
4. ✅ Test with real API key for actual image generation
5. ✅ Review the unit tests in `tests/test_main.py`

## Additional Resources

- **Function Documentation**: See `src/main.py` docstrings
- **API Reference**: https://ai.google.dev/
- **Manifest**: `prefab-manifest.json` for function metadata
- **Main README**: Project root `README.md`
