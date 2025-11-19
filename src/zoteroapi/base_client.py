from typing import Dict, Optional, Any
import requests
from .exceptions import ZoteroLocalError, APIError, ResourceNotFound

class BaseZoteroClient:
    """基础 Zotero 客户端类。
    
    封装 HTTP 请求、错误处理和会话管理的基础类。所有 API 调用
    都通过此类的方法发送 HTTP 请求到 Zotero 本地服务器。
    
    Attributes:
        base_url: Zotero 本地服务器的基础 URL
        _session: requests.Session 对象，用于复用 HTTP 连接
        _cache: 内部缓存字典，用于存储临时数据
        
    Note:
        此类通常不直接使用，而是通过 ZoteroLocal 类使用。
    """
    
    def __init__(self, base_url: str = "http://localhost:23119/api/users/000000/"):
        """初始化基础客户端。
        
        Args:
            base_url: Zotero 本地服务器的基础 URL。默认为
                     'http://localhost:23119/api/users/000000/'。
                     URL 末尾的斜杠会被自动去除。
                     
        Examples:
            >>> # 使用默认 URL
            >>> client = BaseZoteroClient()
            
            >>> # 使用自定义 URL
            >>> client = BaseZoteroClient(
            ...     base_url="http://localhost:23120/api/users/000000/"
            ... )
        """
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._cache = {}
        
    def _make_request(self, 
                     method: str, 
                     endpoint: str,  
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     headers: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> requests.Response:
        """发送 HTTP 请求到 Zotero API。
        
        封装了 HTTP 请求的发送逻辑，自动处理 URL 拼接、参数设置、
        错误处理等。所有请求默认使用 JSON 格式。
        
        Args:
            method: HTTP 方法，如 'GET', 'POST', 'PUT', 'DELETE' 等
            endpoint: API 端点路径，如 '/items', '/collections' 等
            params: URL 查询参数字典，可选
            data: 请求体数据（会被转换为 JSON），可选
            headers: 自定义 HTTP 头，可选
            files: 文件上传数据，可选
            
        Returns:
            requests.Response 对象，包含服务器响应
            
        Raises:
            ZoteroLocalError: 当 HTTP 请求失败或服务器返回错误时抛出
            
        Note:
            - 所有请求默认添加 'format=json' 参数
            - 使用 requests.Session 复用连接，提高性能
            - 自动处理 HTTP 错误状态码
        """
        url = f"{self.base_url}{endpoint}"
        
        params = params or {}
        if 'format' not in params:
            params['format'] = 'json'
            
        headers = headers or {}
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ZoteroLocalError(f"API request failed: {str(e)}")
            
    def _request(self, 
                method: str,
                path: str,
                params: Optional[Dict] = None,
                data: Optional[Dict] = None,
                raw_response: bool = False,
                **kwargs) -> Any:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{path}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                **kwargs
            )
            response.raise_for_status()
            
            if raw_response:
                return response
            
            return response.json() if response.content else None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ResourceNotFound(f"Resource not found: {url}")
            raise APIError(f"Request failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") 