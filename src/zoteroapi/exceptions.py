"""ZoteroAPI 异常类模块。

定义了 ZoteroAPI 中使用的所有异常类。所有异常都继承自
 ZoteroLocalError 基类，便于统一捕获和处理。
"""

class ZoteroLocalError(Exception):
    """基础异常类。
    
    ZoteroAPI 所有异常的基类。可以用于捕获所有 ZoteroAPI 
    相关的错误。
    
    Examples:
        >>> from zoteroapi import ZoteroLocal, ZoteroLocalError
        >>> client = ZoteroLocal()
        >>> try:
        ...     items = client.get_items()
        ... except ZoteroLocalError as e:
        ...     print(f"API 错误: {e}")
    """
    pass

class ConnectionError(ZoteroLocalError):
    """连接错误。
    
    当无法连接到 Zotero 本地服务器时抛出此异常。
    
    常见原因：
    - Zotero 未启动
    - 本地服务器未启用
    - 端口号错误
    - 防火墙阻止访问
    """
    pass

class AuthenticationError(ZoteroLocalError):
    """认证错误。
    
    当 API 请求因认证失败而被拒绝时抛出。
    
    Note:
        Zotero 本地服务器通常不需要认证，此异常较少使用。
    """
    pass

class NotFoundError(ZoteroLocalError):
    """资源未找到错误。
    
    当请求的资源（如文献条目、文献集等）不存在时抛出。
    
    Examples:
        >>> try:
        ...     item = client.get_item("INVALID_KEY")
        ... except NotFoundError:
        ...     print("条目不存在")
    """
    pass

class APIError(ZoteroLocalError):
    """通用 API 错误。
    
    当 API 请求失败但不属于其他特定错误类型时抛出。
    
    包括但不限于：
    - 服务器内部错误 (5xx)
    - 请求参数错误 (4xx)
    - 网络超时
    """
    pass

class ResourceNotFound(ZoteroLocalError):
    """资源不存在异常。
    
    当请求的资源被确认不存在时抛出。与 NotFoundError 类似，
    但更明确地表明资源不存在。
    
    Examples:
        >>> from zoteroapi import ResourceNotFound
        >>> try:
        ...     item = client.get_item("ABC123")
        ... except ResourceNotFound as e:
        ...     print(f"资源未找到: {e}")
    """
    pass 