"""
Zotero Local API Client
~~~~~~~~~~~~~~~~~~~~~~~

一个用于访问本地Zotero服务器API的Python客户端库。

基本用法:
    >>> from zotero_local_api import ZoteroLocal
    >>> client = ZoteroLocal()
    >>> items = client.get_items()
"""

from .client import ZoteroLocal
from .exceptions import (
    ZoteroLocalError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    APIError,
    ResourceNotFound
)

__version__ = "0.1.0"
__all__ = [
    "ZoteroLocal",
    "ZoteroLocalError",
    "ConnectionError", 
    "AuthenticationError",
    "NotFoundError",
    "APIError",
    "ResourceNotFound"
] 