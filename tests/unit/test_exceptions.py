"""
异常类单元测试
"""
import pytest
from zoteroapi.exceptions import (
    ZoteroLocalError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    APIError,
    ResourceNotFound
)


class TestExceptions:
    """异常类测试"""
    
    @pytest.mark.unit
    def test_exception_hierarchy(self):
        """测试异常继承关系 - 所有异常都应继承自 ZoteroLocalError"""
        assert issubclass(ConnectionError, ZoteroLocalError)
        assert issubclass(AuthenticationError, ZoteroLocalError)
        assert issubclass(NotFoundError, ZoteroLocalError)
        assert issubclass(APIError, ZoteroLocalError)
        assert issubclass(ResourceNotFound, ZoteroLocalError)
    
    @pytest.mark.unit
    def test_zotero_local_error(self):
        """测试基础异常 ZoteroLocalError"""
        error_msg = "Test error message"
        exc = ZoteroLocalError(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, Exception)
        
        # 测试可以抛出和捕获
        with pytest.raises(ZoteroLocalError) as exc_info:
            raise ZoteroLocalError(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_connection_error(self):
        """测试连接错误 ConnectionError"""
        error_msg = "Failed to connect to server"
        exc = ConnectionError(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, ZoteroLocalError)
        
        with pytest.raises(ConnectionError) as exc_info:
            raise ConnectionError(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_authentication_error(self):
        """测试认证错误 AuthenticationError"""
        error_msg = "Authentication failed"
        exc = AuthenticationError(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, ZoteroLocalError)
        
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_not_found_error(self):
        """测试资源未找到错误 NotFoundError"""
        error_msg = "Item not found"
        exc = NotFoundError(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, ZoteroLocalError)
        
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_api_error(self):
        """测试 API 错误 APIError"""
        error_msg = "API request failed"
        exc = APIError(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, ZoteroLocalError)
        
        with pytest.raises(APIError) as exc_info:
            raise APIError(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_resource_not_found(self):
        """测试 ResourceNotFound 异常"""
        error_msg = "Resource not found: /api/items/123"
        exc = ResourceNotFound(error_msg)
        
        assert str(exc) == error_msg
        assert isinstance(exc, ZoteroLocalError)
        
        with pytest.raises(ResourceNotFound) as exc_info:
            raise ResourceNotFound(error_msg)
        
        assert str(exc_info.value) == error_msg
    
    @pytest.mark.unit
    def test_catch_base_exception(self):
        """测试可以用基类捕获所有子类异常"""
        # ConnectionError
        with pytest.raises(ZoteroLocalError):
            raise ConnectionError("Connection failed")
        
        # AuthenticationError
        with pytest.raises(ZoteroLocalError):
            raise AuthenticationError("Auth failed")
        
        # NotFoundError
        with pytest.raises(ZoteroLocalError):
            raise NotFoundError("Not found")
        
        # APIError
        with pytest.raises(ZoteroLocalError):
            raise APIError("API failed")
        
        # ResourceNotFound
        with pytest.raises(ZoteroLocalError):
            raise ResourceNotFound("Resource not found")
    
    @pytest.mark.unit
    def test_exception_with_empty_message(self):
        """测试空消息的异常"""
        exc = ZoteroLocalError("")
        assert str(exc) == ""
        
        exc = APIError("")
        assert str(exc) == ""
    
    @pytest.mark.unit
    def test_exception_with_special_characters(self):
        """测试包含特殊字符的异常消息"""
        special_msg = "Error: 文献集不存在 (Collection not found) 😕"
        exc = ZoteroLocalError(special_msg)
        assert str(exc) == special_msg
    
    @pytest.mark.unit
    def test_exception_repr(self):
        """测试异常的字符串表示"""
        error_msg = "Test error"
        exc = ZoteroLocalError(error_msg)
        
        # 检查异常的 repr 包含类名和消息
        repr_str = repr(exc)
        assert "ZoteroLocalError" in repr_str
        assert error_msg in repr_str
