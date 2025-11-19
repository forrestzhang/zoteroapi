"""
BaseZoteroClient 单元测试
"""
import pytest
import requests
from unittest.mock import patch
from zoteroapi.base_client import BaseZoteroClient
from zoteroapi.exceptions import ZoteroLocalError, APIError, ResourceNotFound


class TestBaseZoteroClient:
    """BaseZoteroClient 测试类"""
    
    def test_client_init_default(self):
        """测试默认初始化"""
        client = BaseZoteroClient()
        assert client.base_url == "http://localhost:23119/api/users/000000"
        assert client._session is not None
        assert isinstance(client._session, requests.Session)
    
    def test_client_init_custom_url(self):
        """测试自定义 URL 初始化"""
        custom_url = "http://custom.server:8080/api/users/123456/"
        client = BaseZoteroClient(custom_url)
        # 应该去除末尾的斜杠
        assert client.base_url == "http://custom.server:8080/api/users/123456"
    
    def test_client_init_url_trailing_slash(self):
        """测试 URL 末尾斜杠处理"""
        url_with_slash = "http://localhost:23119/api/users/000000/"
        url_without_slash = "http://localhost:23119/api/users/000000"
        
        client1 = BaseZoteroClient(url_with_slash)
        client2 = BaseZoteroClient(url_without_slash)
        
        assert client1.base_url == client2.base_url
    
    @pytest.mark.unit
    def test_make_request_success(self, requests_mock):
        """测试成功的 API 请求"""
        client = BaseZoteroClient()
        test_data = {"key": "TEST123", "data": {"title": "Test Item"}}
        
        requests_mock.get(
            f"{client.base_url}/items/TEST123",
            json=test_data,
            status_code=200
        )
        
        response = client._make_request("GET", "/items/TEST123")
        
        assert response.status_code == 200
        assert response.json() == test_data
    
    @pytest.mark.unit
    def test_make_request_with_params(self, requests_mock):
        """测试带查询参数的请求"""
        client = BaseZoteroClient()
        test_data = [{"key": "ITEM1"}, {"key": "ITEM2"}]
        
        # 使用 complete_qs=False 以匹配任何查询参数
        requests_mock.get(
            f"{client.base_url}/items",
            json=test_data,
            status_code=200
        )
        
        response = client._make_request("GET", "/items", params={"limit": 10})
        
        assert response.status_code == 200
        # 验证请求包含查询参数
        assert "limit=10" in requests_mock.last_request.url
        assert "format=json" in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_make_request_auto_format(self, requests_mock):
        """测试自动添加 format 参数"""
        client = BaseZoteroClient()
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=[],
            status_code=200
        )
        
        client._make_request("GET", "/items")
        
        # 验证自动添加了 format=json
        assert "format=json" in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_make_request_custom_format(self, requests_mock):
        """测试自定义 format 参数"""
        client = BaseZoteroClient()
        
        requests_mock.get(
            f"{client.base_url}/items",
            text="<xml>data</xml>",
            status_code=200
        )
        
        client._make_request("GET", "/items", params={"format": "atom"})
        
        # 验证使用了自定义的 format
        assert "format=atom" in requests_mock.last_request.url
        assert "format=json" not in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_make_request_http_error(self, requests_mock):
        """测试 HTTP 错误处理"""
        client = BaseZoteroClient()
        
        requests_mock.get(
            f"{client.base_url}/items/NOTFOUND",
            status_code=404,
            json={"error": "Not Found"}
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client._make_request("GET", "/items/NOTFOUND")
        
        assert "API request failed" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_make_request_with_data(self, requests_mock):
        """测试带数据的 POST 请求"""
        client = BaseZoteroClient()
        test_data = {"items": [{"itemType": "note", "note": "Test"}]}
        response_data = {"successful": [{"key": "NEW123"}]}
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=response_data,
            status_code=201
        )
        
        response = client._make_request("POST", "/items", data=test_data)
        
        assert response.status_code == 201
        assert response.json() == response_data
        # 验证发送的数据
        assert requests_mock.last_request.json() == test_data
    
    @pytest.mark.unit
    def test_make_request_with_headers(self, requests_mock):
        """测试带自定义头的请求"""
        client = BaseZoteroClient()
        custom_headers = {"X-Custom-Header": "test-value"}
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=[],
            status_code=200
        )
        
        client._make_request("GET", "/items", headers=custom_headers)
        
        assert requests_mock.last_request.headers.get("X-Custom-Header") == "test-value"
    
    @pytest.mark.unit
    def test_request_method_raw_response(self, requests_mock):
        """测试 raw_response=True 返回原始响应"""
        client = BaseZoteroClient()
        test_data = {"key": "TEST123"}
        
        requests_mock.get(
            f"{client.base_url}/items/TEST123",
            json=test_data,
            status_code=200
        )
        
        response = client._request("GET", "/items/TEST123", raw_response=True)
        
        assert isinstance(response, requests.Response)
        assert response.json() == test_data
    
    @pytest.mark.unit
    def test_request_method_json_response(self, requests_mock):
        """测试默认返回 JSON 数据"""
        client = BaseZoteroClient()
        test_data = {"key": "TEST123"}
        
        requests_mock.get(
            f"{client.base_url}/items/TEST123",
            json=test_data,
            status_code=200
        )
        
        result = client._request("GET", "/items/TEST123")
        
        assert result == test_data
    
    @pytest.mark.unit
    def test_request_method_404_error(self, requests_mock):
        """测试 404 错误处理，应抛出 ResourceNotFound"""
        client = BaseZoteroClient()
        
        requests_mock.get(
            f"{client.base_url}/items/NOTFOUND",
            status_code=404,
            json={"error": "Not Found"}
        )
        
        with pytest.raises(ResourceNotFound) as exc_info:
            client._request("GET", "/items/NOTFOUND")
        
        assert "Resource not found" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_request_method_500_error(self, requests_mock):
        """测试 500 错误处理，应抛出 APIError"""
        client = BaseZoteroClient()
        
        requests_mock.get(
            f"{client.base_url}/items",
            status_code=500,
            json={"error": "Internal Server Error"}
        )
        
        with pytest.raises(APIError) as exc_info:
            client._request("GET", "/items")
        
        assert "Request failed" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_request_method_empty_response(self, requests_mock):
        """测试空响应处理"""
        client = BaseZoteroClient()
        
        requests_mock.delete(
            f"{client.base_url}/items/TEST123",
            status_code=204,
            text=""
        )
        
        result = client._request("DELETE", "/items/TEST123")
        
        assert result is None
    
    @pytest.mark.unit
    def test_session_persistence(self):
        """测试 Session 对象在多次请求中复用"""
        client = BaseZoteroClient()
        session1 = client._session
        session2 = client._session
        
        assert session1 is session2
        assert id(session1) == id(session2)
    
    @pytest.mark.unit
    def test_make_request_network_error(self):
        """测试网络错误处理"""
        client = BaseZoteroClient()
        
        with patch.object(client._session, 'request') as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError("Network error")
            
            with pytest.raises(ZoteroLocalError) as exc_info:
                client._make_request("GET", "/items")
            
            assert "API request failed" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_cache_attribute_exists(self):
        """测试 _cache 属性存在"""
        client = BaseZoteroClient()
        assert hasattr(client, '_cache')
        assert isinstance(client._cache, dict)
