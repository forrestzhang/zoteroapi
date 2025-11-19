# 异常类

ZoteroAPI 定义了一套完整的异常类层次结构，所有异常都继承自 `ZoteroLocalError` 基类，便于统一捕获和处理各种错误情况。

## 异常层次结构

```
ZoteroLocalError (基类)
├── ConnectionError     # 连接错误
├── AuthenticationError # 认证错误
├── NotFoundError       # 资源未找到错误
├── APIError           # 通用 API 错误
└── ResourceNotFound   # 资源不存在异常
```

## 基础异常类

### ZoteroLocalError

```python
class ZoteroLocalError(Exception):
    """
    基础异常类

    ZoteroAPI 所有异常的基类。可以用于捕获所有 ZoteroAPI
    相关的错误。

    Attributes:
        message: 错误信息
        original_error: 原始异常对象（如果有）

    Examples:
        >>> from zoteroapi import ZoteroLocal, ZoteroLocalError
        >>> client = ZoteroLocal()
        >>> try:
        ...     items = client.get_items()
        ... except ZoteroLocalError as e:
        ...     print(f"API 错误: {e}")
    """
```

### 连接相关异常

#### ConnectionError

```python
class ConnectionError(ZoteroLocalError):
    """
    连接错误

    当无法连接到 Zotero 本地服务器时抛出此异常。

    常见原因：
    - Zotero 未启动
    - 本地服务器未启用
    - 端口号错误
    - 防火墙阻止访问
    - 网络连接问题

    Examples:
        >>> from zoteroapi import ConnectionError
        >>> try:
        ...     client = ZoteroLocal()
        ...     items = client.get_items()
        ... except ConnectionError:
        ...     print("无法连接到 Zotero，请检查：")
        ...     print("1. Zotero 是否正在运行")
        ...     print("2. 本地服务器是否已启用")
        ...     print("3. 端口 23119 是否被占用")

    Note:
        检查 Zotero 首选项中的服务器设置
        验证防火墙是否阻止了本地端口访问
    """
```

#### AuthenticationError

```python
class AuthenticationError(ZoteroLocalError):
    """
    认证错误

    当 API 请求因认证失败而被拒绝时抛出。

    Note:
        Zotero 本地服务器通常不需要认证，此异常较少使用
        主要用于将来的扩展功能或特殊配置

    Examples:
        >>> from zoteroapi import AuthenticationError
        >>> try:
        ...     # 需要认证的 API 调用
        ...     pass
        ... except AuthenticationError:
        ...     print("认证失败，请检查访问权限")
    """
```

### 资源相关异常

#### NotFoundError

```python
class NotFoundError(ZoteroLocalError):
    """
    资源未找到错误

    当请求的资源（如文献条目、文献集等）不存在时抛出。

    Examples:
        >>> from zoteroapi import NotFoundError
        >>> try:
        ...     item = client.get_item("INVALID_KEY")
        ... except NotFoundError:
        ...     print("条目不存在")
        ...     # 可以提供用户友好的错误处理
        ...     print("请检查条目 key 是否正确")

    Note:
        与 ResourceNotFound 类似，但更通用
        用于各种资源不存在的情况
    """
```

#### ResourceNotFound

```python
class ResourceNotFound(ZoteroLocalError):
    """
    资源不存在异常

    当请求的资源被确认不存在时抛出。与 NotFoundError 类似，
    但更明确地表明资源不存在。

    Examples:
        >>> from zoteroapi import ResourceNotFound
        >>> try:
        ...     item = client.get_item("ABC123")
        ... except ResourceNotFound as e:
        ...     print(f"资源未找到: {e}")

    Note:
        通常在 API 明确返回 404 状态码时使用
        比 NotFoundError 更具体
    """
```

### API 相关异常

#### APIError

```python
class APIError(ZoteroLocalError):
    """
    通用 API 错误

    当 API 请求失败但不属于其他特定错误类型时抛出。

    包括但不限于：
    - 服务器内部错误 (5xx)
    - 请求参数错误 (4xx)
    - 网络超时
    - 数据格式错误

    Attributes:
        status_code: HTTP 状态码（如果有）
        response: 原始响应对象（如果有）

    Examples:
        >>> from zoteroapi import APIError
        >>> try:
        ...     result = client.some_api_call()
        ... except APIError as e:
        ...     print(f"API 错误: {e}")
        ...     if hasattr(e, 'status_code'):
        ...         print(f"HTTP 状态码: {e.status_code}")

    Note:
        适用于各种未分类的 API 错误
        可以通过检查具体错误信息进行针对性处理
    """
```

## 使用示例

### 基础错误处理

```python
from zoteroapi import ZoteroLocal, ZoteroLocalError, ResourceNotFound

def safe_get_item(client, item_key):
    """安全获取文献条目"""
    try:
        return client.get_item(item_key)
    except ResourceNotFound:
        print(f"文献 {item_key} 不存在")
        return None
    except ConnectionError:
        print("无法连接到 Zotero")
        return None
    except ZoteroLocalError as e:
        print(f"获取文献失败: {e}")
        return None

# 使用
client = ZoteroLocal()
item = safe_get_item(client, "ITEM_KEY_HERE")
```

### 分层错误处理

```python
def advanced_error_handling():
    """分层的错误处理"""
    client = ZoteroLocal()

    try:
        # 执行多个操作
        items = client.get_items_top(limit=10)
        for item in items:
            try:
                notes = client.get_item_notes(item['key'])
                print(f"文献 {item['key']} 有 {len(notes)} 条笔记")
            except ResourceNotFound:
                print(f"文献 {item['key']} 的笔记不存在")
            except APIError as e:
                print(f"获取笔记时 API 错误: {e}")

    except ConnectionError:
        print("连接失败，请检查 Zotero 设置")
    except ZoteroLocalError as e:
        print(f"操作失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
```

### 错误恢复机制

```python
import time
from typing import Callable, Any

def retry_with_backoff(func: Callable, max_retries: int = 3, *args, **kwargs) -> Any:
    """带指数退避的重试机制"""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (ConnectionError, APIError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"操作失败，{wait_time} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                break
        except ResourceNotFound:
            # 资源不存在不需要重试
            raise

    raise last_exception

# 使用
def get_item_with_retry(client, item_key):
    try:
        return retry_with_backoff(client.get_item, max_retries=3, item_key=item_key)
    except (ConnectionError, APIError) as e:
        print(f"多次重试后仍然失败: {e}")
        return None
```

### 用户友好的错误提示

```python
class UserFriendlyErrorHandler:
    """用户友好的错误处理器"""

    @staticmethod
    def format_error_message(exception: Exception) -> str:
        """格式化错误信息"""
        if isinstance(exception, ConnectionError):
            return (
                "无法连接到 Zotero 本地服务器。请检查：\n"
                "1. Zotero 是否正在运行\n"
                "2. 编辑 → 首选项 → 高级 → 配置编辑器中\n"
                "   extensions.zotero.httpServer.enabled 是否为 true\n"
                "3. 端口 23119 是否被其他程序占用"
            )
        elif isinstance(exception, ResourceNotFound):
            return "请求的文献或资源不存在。请检查标识符是否正确。"
        elif isinstance(exception, AuthenticationError):
            return "认证失败。请检查访问权限设置。"
        elif isinstance(exception, APIError):
            return f"API 请求失败: {str(exception)}"
        elif isinstance(exception, ZoteroLocalError):
            return f"Zotero 操作失败: {str(exception)}"
        else:
            return f"未知错误: {str(exception)}"

    @staticmethod
    def handle_error(exception: Exception, show_traceback: bool = False):
        """处理异常并显示用户友好的信息"""
        user_message = UserFriendlyErrorHandler.format_error_message(exception)
        print(f"错误: {user_message}")

        if show_traceback:
            import traceback
            print("\n详细错误信息:")
            traceback.print_exc()

# 使用
try:
    client = ZoteroLocal()
    items = client.get_items()
except Exception as e:
    UserFriendlyErrorHandler.handle_error(e, show_traceback=False)
```

### 异常日志记录

```python
import logging
from datetime import datetime

class ExceptionLogger:
    """异常日志记录器"""

    def __init__(self, log_file: str = "zoteroapi_errors.log"):
        self.logger = logging.getLogger("zoteroapi")
        self.logger.setLevel(logging.ERROR)

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_exception(self, exception: Exception, context: str = ""):
        """记录异常信息"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'context': context
        }

        self.logger.error(f"Exception in {context}: {error_info}", exc_info=True)

# 使用
logger = ExceptionLogger()

try:
    client = ZoteroLocal()
    items = client.get_items()
except Exception as e:
    logger.log_exception(e, "getting items")
```

## 自定义异常

### 创建自定义异常类

```python
class ZoteroAPIValidationError(ZoteroLocalError):
    """数据验证错误"""
    pass

class ZoteroAPIRateLimitError(ZoteroLocalError):
    """API 速率限制错误"""
    pass

class ZoteroAPIConfigurationError(ZoteroLocalError):
    """配置错误"""
    pass

def validate_item_key(item_key: str):
    """验证条目 key 格式"""
    if not item_key:
        raise ZoteroAPIValidationError("条目 key 不能为空")
    if len(item_key) != 8:
        raise ZoteroAPIValidationError("条目 key 长度必须为 8 字符")
    if not item_key.isalnum():
        raise ZoteroAPIValidationError("条目 key 只能包含字母和数字")
```

### 异常链式处理

```python
class ChainedExceptionExample:
    def __init__(self, client):
        self.client = client

    def get_item_with_context(self, item_key: str, operation: str):
        """带上下文的异常处理"""
        try:
            return self.client.get_item(item_key)
        except ResourceNotFound as e:
            # 添加上下文信息后重新抛出
            raise ZoteroLocalError(
                f"在 {operation} 操作中找不到文献 {item_key}"
            ) from e
        except ConnectionError as e:
            raise ZoteroLocalError(
                f"在 {operation} 操作中连接失败"
            ) from e
```

## 最佳实践

### 1. 异常处理原则

```python
# ✅ 推荐：具体的异常处理
try:
    item = client.get_item(item_key)
except ResourceNotFound:
    print("文献不存在")
except ConnectionError:
    print("连接失败")
except ZoteroLocalError as e:
    print(f"API 错误: {e}")

# ❌ 不推荐：过于宽泛的异常处理
try:
    item = client.get_item(item_key)
except Exception:
    print("出错了")
```

### 2. 异常信息记录

```python
# ✅ 推荐：记录详细的异常信息
import logging

logger = logging.getLogger(__name__)

try:
    item = client.get_item(item_key)
except ZoteroLocalError as e:
    logger.error(f"获取文献失败: {item_key}", exc_info=True)
    raise

# ❌ 不推荐：忽略异常信息
try:
    item = client.get_item(item_key)
except:
    pass
```

### 3. 资源清理

```python
# ✅ 推荐：确保资源清理
try:
    client = ZoteroLocal()
    items = client.get_items()
    # 处理 items
finally:
    # 清理资源（如果需要）
    pass

# 使用上下文管理器（如果支持）
# with ZoteroLocal() as client:
#     items = client.get_items()
```

通过合理使用这些异常类和错误处理模式，可以构建更稳定和用户友好的应用程序。