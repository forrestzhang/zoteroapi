class ZoteroLocalError(Exception):
    """Zotero本地API异常基类"""
    pass

class ConnectionError(ZoteroLocalError):
    """连接错误"""
    pass

class AuthenticationError(ZoteroLocalError):
    """认证错误"""
    pass

class NotFoundError(ZoteroLocalError):
    """资源未找到"""
    pass

class APIError(ZoteroLocalError):
    """API错误"""
    pass

class ResourceNotFound(ZoteroLocalError):
    """Raised when a requested resource is not found"""
    pass 