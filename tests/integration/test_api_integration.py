"""
API 集成测试
"""
import pytest
from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError, APIError, ResourceNotFound


class TestAPIIntegration:
    """API 集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_api_connection(self, requests_mock):
        """测试 API 连接性"""
        client = ZoteroLocal()
        
        # Mock 一个简单的 API 请求
        requests_mock.get(
            f"{client.base_url}/items",
            json=[],
            status_code=200
        )
        
        result = client.get_items()
        
        assert isinstance(result, list)
    
    @pytest.mark.integration
    def test_api_error_responses(self, requests_mock):
        """测试各种 HTTP 错误码的处理"""
        client = ZoteroLocal()
        
        # 测试 404 错误
        requests_mock.get(
            f"{client.base_url}/items/NOTFOUND",
            status_code=404,
            json={"error": "Not Found"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.get_item("NOTFOUND")
        
        # 测试 500 错误
        requests_mock.get(
            f"{client.base_url}/items/ERROR",
            status_code=500,
            json={"error": "Internal Server Error"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.get_item("ERROR")
        
        # 测试 400 错误
        requests_mock.post(
            f"{client.base_url}/items",
            status_code=400,
            json={"error": "Bad Request"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client._make_request("POST", "/items", data={"invalid": "data"})
    
    @pytest.mark.integration
    def test_concurrent_requests(self, requests_mock):
        """测试并发请求 - Session 复用的线程安全性"""
        client = ZoteroLocal()
        
        # 准备多个 Mock 端点
        for i in range(5):
            requests_mock.get(
                f"{client.base_url}/items/ITEM{i}",
                json={"key": f"ITEM{i}"},
                status_code=200
            )
        
        # 连续发送多个请求
        results = []
        for i in range(5):
            result = client.get_item(f"ITEM{i}")
            results.append(result)
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["key"] == f"ITEM{i}"
    
    @pytest.mark.integration
    def test_session_reuse(self):
        """测试 Session 对象在多次请求间复用"""
        client = ZoteroLocal()
        
        session1 = client._session
        session2 = client._session
        
        assert session1 is session2
    
    @pytest.mark.integration
    def test_api_response_format(self, requests_mock):
        """测试 API 响应格式一致性"""
        client = ZoteroLocal()
        
        # 标准的 Zotero API 响应格式
        standard_response = {
            "key": "TEST123",
            "version": 1,
            "data": {
                "itemType": "journalArticle",
                "title": "Test Article"
            }
        }
        
        requests_mock.get(
            f"{client.base_url}/items/TEST123",
            json=standard_response,
            status_code=200
        )
        
        result = client.get_item("TEST123")
        
        # 验证响应包含标准字段
        assert "key" in result
        assert "version" in result
        assert "data" in result
        assert "itemType" in result["data"]
    
    @pytest.mark.integration
    def test_error_message_propagation(self, requests_mock):
        """测试错误消息正确传播"""
        client = ZoteroLocal()
        
        error_message = "Custom error from API"
        requests_mock.get(
            f"{client.base_url}/items/ERROR",
            status_code=500,
            json={"error": error_message}
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.get_item("ERROR")
        
        # 错误信息应该被捕获并包装
        assert isinstance(exc_info.value, ZoteroLocalError)
    
    @pytest.mark.integration
    def test_multiple_client_instances(self):
        """测试多个客户端实例独立工作"""
        client1 = ZoteroLocal()
        client2 = ZoteroLocal("http://localhost:23119/api/users/111111/")
        
        assert client1.base_url != client2.base_url
        assert client1._session is not client2._session
    
    @pytest.mark.integration
    def test_request_with_various_methods(self, requests_mock):
        """测试不同 HTTP 方法的请求"""
        client = ZoteroLocal()
        
        # GET
        requests_mock.get(
            f"{client.base_url}/items",
            json=[],
            status_code=200
        )
        
        result = client._make_request("GET", "/items")
        assert result.status_code == 200
        
        # POST
        requests_mock.post(
            f"{client.base_url}/items",
            json={"success": True},
            status_code=201
        )
        
        result = client._make_request("POST", "/items", data={"test": "data"})
        assert result.status_code == 201
        
        # DELETE (如果 API 支持)
        requests_mock.delete(
            f"{client.base_url}/items/TEST123",
            status_code=204
        )
        
        result = client._make_request("DELETE", "/items/TEST123")
        assert result.status_code == 204
