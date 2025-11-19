# BaseZoteroClient

`BaseZoteroClient` 是 ZoteroAPI 的基础 HTTP 客户端类，负责处理与 Zotero 本地服务器的所有 HTTP 通信。它提供了底层的请求处理、错误管理和会话管理功能。

## 类定义

```python
class BaseZoteroClient:
    """基础 Zotero 客户端类"""
```

## 构造函数

```python
def __init__(self, base_url: str = "http://localhost:23119/api/users/000000/"):
    """
    初始化基础客户端

    Args:
        base_url: Zotero 本地服务器的基础 URL
                 默认: "http://localhost:23119/api/users/000000/"

    Examples:
        >>> client = BaseZoteroClient()
        >>> client = BaseZoteroClient("http://localhost:23120/api/users/000000/")
    """
```

## 主要方法

### _make_request()

```python
def _make_request(self,
                 method: str,
                 endpoint: str,
                 params: Optional[Dict] = None,
                 data: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 files: Optional[Dict] = None) -> requests.Response:
    """
    发送 HTTP 请求到 Zotero API

    Args:
        method: HTTP 方法，如 'GET', 'POST', 'PUT', 'DELETE' 等
        endpoint: API 端点路径，如 '/items', '/collections' 等
        params: URL 查询参数字典，可选
        data: 请求体数据（会被转换为 JSON），可选
        headers: 自定义 HTTP 头，可选
        files: 文件上传数据，可选

    Returns:
        requests.Response: 包含服务器响应的 Response 对象

    Raises:
        ZoteroLocalError: 当 HTTP 请求失败或服务器返回错误时抛出

    Note:
        - 所有请求默认添加 'format=json' 参数
        - 使用 requests.Session 复用连接，提高性能
        - 自动处理 HTTP 错误状态码
    """
```

### _request()

```python
def _request(self,
            method: str,
            path: str,
            params: Optional[Dict] = None,
            data: Optional[Dict] = None,
            raw_response: bool = False,
            **kwargs) -> Any:
    """
    发送 HTTP 请求并处理响应

    Args:
        method: HTTP 方法
        path: API 路径
        params: URL 查询参数
        data: 请求体数据
        raw_response: 是否返回原始 Response 对象
        **kwargs: 其他 requests 参数

    Returns:
        Any: JSON 数据或 Response 对象

    Raises:
        ResourceNotFound: 当资源不存在时（404 状态码）
        APIError: 当 API 请求失败时
    """
```

## 属性

### base_url

```python
@property
def base_url(self) -> str:
    """获取基础 URL"""
    return self._base_url

@base_url.setter
def base_url(self, value: str):
    """设置基础 URL，自动去除末尾斜杠"""
    self._base_url = value.rstrip('/')
```

### session

```python
@property
def session(self) -> requests.Session:
    """获取 HTTP 会话对象"""
    return self._session
```

## 工作原理

### HTTP 会话管理

`BaseZoteroClient` 使用 `requests.Session` 来管理 HTTP 连接：

```python
# 连接复用
session = requests.Session()

# 所有请求共享连接池
response1 = session.get(url1)
response2 = session.get(url2)  # 复用连接
```

### 请求处理流程

1. **URL 构建**: 将基础 URL 和端点路径组合
2. **参数处理**: 自动添加 `format=json` 参数
3. **请求发送**: 使用 Session 对象发送请求
4. **错误处理**: 自动处理 HTTP 错误状态码
5. **响应返回**: 返回 Response 对象供上层处理

### 错误处理机制

```python
try:
    response = self._session.request(...)
    response.raise_for_status()  # 抛出 HTTP 错误
    return response
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        raise ResourceNotFound(f"Resource not found: {url}")
    raise APIError(f"Request failed: {str(e)}")
except requests.exceptions.RequestException as e:
    raise APIError(f"Request failed: {str(e)}")
```

## 使用示例

### 直接使用基础客户端

```python
from zoteroapi.base_client import BaseZoteroClient

# 创建基础客户端
client = BaseZoteroClient()

# 获取所有文献条目
response = client._make_request("GET", "/items", params={"limit": 10})
items = response.json()

# 获取特定文献
item_response = client._make_request("GET", "/items/ABC123")
item = item_response.json()

# 创建新条目
new_item_data = {
    "items": [{
        "itemType": "journalArticle",
        "title": "新论文标题"
    }]
}
create_response = client._make_request(
    "POST",
    "/items",
    data=new_item_data
)
```

### 自定义请求头

```python
# 添加自定义请求头
headers = {
    "User-Agent": "MyApp/1.0",
    "Accept": "application/json"
}

response = client._make_request(
    "GET",
    "/items",
    headers=headers
)
```

### 文件上传

```python
# 上传文件
files = {
    "file": open("paper.pdf", "rb")
}

response = client._make_request(
    "POST",
    "/items/ITEM_KEY/file",
    files=files
)
files["file"].close()  # 记得关闭文件
```

### 原始响应处理

```python
# 获取原始响应对象
response = client._request(
    "GET",
    "/items/ITEM_KEY/file",
    raw_response=True,
    params={"format": "raw"}
)

# 访问响应头
content_type = response.headers.get('Content-Type')
content_length = response.headers.get('Content-Length')

# 保存文件
with open("downloaded_file.pdf", "wb") as f:
    f.write(response.content)
```

## 扩展功能

### 自定义客户端类

```python
class CustomZoteroClient(BaseZoteroClient):
    """自定义 Zotero 客户端"""

    def custom_search(self, query: str) -> list:
        """自定义搜索方法"""
        params = {
            "q": query,
            "format": "json",
            "limit": 50
        }

        response = self._make_request("GET", "/items", params=params)
        return response.json()

    def batch_operations(self, operations: list) -> list:
        """批量操作"""
        results = []
        for operation in operations:
            method = operation.get("method", "GET")
            endpoint = operation.get("endpoint", "/")
            data = operation.get("data")

            try:
                response = self._make_request(method, endpoint, data=data)
                results.append({"success": True, "data": response.json()})
            except Exception as e:
                results.append({"success": False, "error": str(e)})

        return results

# 使用自定义客户端
client = CustomZoteroClient()
results = client.custom_search("machine learning")
```

### 重试机制

```python
import time
from typing import Callable, Any

class RetryableZoteroClient(BaseZoteroClient):
    """带重试机制的客户端"""

    def _make_request_with_retry(self,
                                method: str,
                                endpoint: str,
                                max_retries: int = 3,
                                **kwargs) -> requests.Response:
        """带重试的请求方法"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return self._make_request(method, endpoint, **kwargs)
            except ZoteroLocalError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"请求失败，{wait_time} 秒后重试...")
                    time.sleep(wait_time)

        raise last_exception
```

### 请求日志

```python
import logging
from datetime import datetime

class LoggingZoteroClient(BaseZoteroClient):
    """带日志功能的客户端"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def _make_request(self, *args, **kwargs) -> requests.Response:
        """重写请求方法添加日志"""
        start_time = datetime.now()
        method = args[0] if args else kwargs.get('method', 'GET')
        endpoint = args[1] if len(args) > 1 else kwargs.get('endpoint', '/')

        self.logger.info(f"发送请求: {method} {endpoint}")

        try:
            response = super()._make_request(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"请求成功: {response.status_code} "
                f"({duration:.3f}s, {len(response.content)} bytes)"
            )

            return response

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"请求失败: {method} {endpoint} "
                f"({duration:.3f}s) - {str(e)}"
            )
            raise
```

## 性能优化

### 连接池配置

```python
# 自定义会话配置
import requests.adapters

client = BaseZoteroClient()

# 配置连接池
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)

client.session.mount('http://', adapter)
client.session.mount('https://', adapter)
```

### 请求缓存

```python
from functools import lru_cache
import hashlib

class CachedZoteroClient(BaseZoteroClient):
    """带缓存功能的客户端"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def _make_request(self, *args, **kwargs):
        """带缓存的请求方法"""
        # 生成缓存键
        cache_key = self._generate_cache_key(*args, **kwargs)

        # 检查缓存
        if cache_key in self._cache:
            cached_response = self._cache[cache_key]
            if not self._is_cache_expired(cached_response):
                return cached_response['data']

        # 发送请求
        response = super()._make_request(*args, **kwargs)

        # 缓存响应
        self._cache[cache_key] = {
            'data': response,
            'timestamp': datetime.now()
        }

        return response

    def _generate_cache_key(self, method: str, endpoint: str, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{method}:{endpoint}:{str(kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()
```

## 注意事项

1. **线程安全**: `BaseZoteroClient` 不是线程安全的，多线程环境下需要为每个线程创建实例
2. **资源管理**: 虽然 Session 会自动管理连接，但建议在程序结束时清理资源
3. **错误处理**: 总是处理可能的 `ZoteroLocalError` 异常
4. **请求限制**: 避免过于频繁的请求，可能导致 Zotero 服务器响应缓慢
5. **内存使用**: 大文件操作时注意内存使用，及时处理响应内容

`BaseZoteroClient` 提供了稳定可靠的 HTTP 通信基础，所有上层功能都构建在这个基础之上。