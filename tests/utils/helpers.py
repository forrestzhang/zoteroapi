"""
测试辅助函数
"""
import json
from typing import Any, Dict


def assert_dict_contains(actual: Dict, expected: Dict, path: str = "") -> None:
    """
    断言实际字典包含期望的键值对
    
    Args:
        actual: 实际的字典
        expected: 期望包含的键值对
        path: 当前检查路径（用于错误消息）
    """
    for key, value in expected.items():
        current_path = f"{path}.{key}" if path else key
        
        assert key in actual, f"Key '{current_path}' not found in actual dict"
        
        if isinstance(value, dict) and isinstance(actual[key], dict):
            assert_dict_contains(actual[key], value, current_path)
        else:
            assert actual[key] == value, \
                f"Value mismatch at '{current_path}': expected {value}, got {actual[key]}"


def create_mock_response(data: Any, status_code: int = 200, headers: Dict = None):
    """
    创建一个模拟的 requests.Response 对象
    
    Args:
        data: 响应数据
        status_code: HTTP 状态码
        headers: 响应头
        
    Returns:
        模拟的 Response 对象
    """
    from unittest.mock import Mock
    
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {"Content-Type": "application/json"}
    
    if isinstance(data, (dict, list)):
        response.json.return_value = data
        response.content = json.dumps(data).encode()
        response.text = json.dumps(data)
    else:
        response.content = data if isinstance(data, bytes) else str(data).encode()
        response.text = data if isinstance(data, str) else str(data)
    
    if status_code >= 400:
        response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    else:
        response.raise_for_status.return_value = None
    
    return response
