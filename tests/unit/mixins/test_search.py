"""
SearchMixin 单元测试
"""
import pytest
from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError
from tests.fixtures.mock_data import MockDataFactory, SAMPLE_ITEMS


class TestSearchMixin:
    """搜索功能测试"""
    
    @pytest.mark.unit
    def test_search_items(self, requests_mock):
        """测试关键词搜索"""
        client = ZoteroLocal()
        query = "python"
        search_results = [SAMPLE_ITEMS[0]]
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=search_results,
            status_code=200
        )
        
        result = client.search_items(query)
        
        assert isinstance(result, list)
        assert len(result) == 1
        # 验证请求包含查询参数
        assert f"q={query}" in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_search_items_no_results(self, requests_mock):
        """测试搜索无结果"""
        client = ZoteroLocal()
        query = "nonexistent"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=[],
            status_code=200
        )
        
        result = client.search_items(query)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_search_by_doi(self, requests_mock):
        """测试 DOI 搜索 - 精确匹配"""
        client = ZoteroLocal()
        target_doi = "10.1234/python.001"
        
        # Mock get_items 返回所有条目
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_doi(target_doi)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["data"]["DOI"] == target_doi
    
    @pytest.mark.unit
    def test_search_by_doi_case_insensitive(self, requests_mock):
        """测试 DOI 搜索 - 大小写不敏感"""
        client = ZoteroLocal()
        target_doi = "10.1234/PYTHON.001"  # 大写
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_doi(target_doi)
        
        assert len(result) == 1
        # 应该匹配到小写的 DOI
        assert result[0]["data"]["DOI"].lower() == target_doi.lower()
    
    @pytest.mark.unit
    def test_search_by_doi_no_match(self, requests_mock):
        """测试 DOI 无匹配"""
        client = ZoteroLocal()
        target_doi = "10.9999/nonexistent"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_doi(target_doi)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_search_by_pmid(self, requests_mock):
        """测试 PMID 搜索"""
        client = ZoteroLocal()
        target_pmid = "11111111"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_pmid(target_pmid)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert target_pmid in result[0]["data"]["extra"]
    
    @pytest.mark.unit
    def test_search_by_pmid_no_match(self, requests_mock):
        """测试 PMID 无匹配"""
        client = ZoteroLocal()
        target_pmid = "99999999"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_pmid(target_pmid)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_search_by_title_exact(self, requests_mock):
        """测试标题精确匹配"""
        client = ZoteroLocal()
        target_title = "Python Programming"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_title(target_title, exact_match=True)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["data"]["title"] == target_title
    
    @pytest.mark.unit
    def test_search_by_title_partial(self, requests_mock):
        """测试标题部分匹配"""
        client = ZoteroLocal()
        partial_title = "Learning"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_title(partial_title, exact_match=False)
        
        assert isinstance(result, list)
        # 应该匹配到 "Machine Learning Basics" 和 "Deep Learning Advanced"
        assert len(result) == 2
        for item in result:
            assert "Learning" in item["data"]["title"]
    
    @pytest.mark.unit
    def test_search_by_title_case_insensitive(self, requests_mock):
        """测试标题搜索忽略大小写"""
        client = ZoteroLocal()
        target_title = "python programming"  # 小写
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_title(target_title, exact_match=True)
        
        assert len(result) == 1
        assert result[0]["data"]["title"].lower() == target_title
    
    @pytest.mark.unit
    def test_search_by_title_no_match(self, requests_mock):
        """测试标题无匹配"""
        client = ZoteroLocal()
        target_title = "Nonexistent Title"
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_title(target_title)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_search_by_title_empty_string(self, requests_mock):
        """测试空字符串搜索"""
        client = ZoteroLocal()
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.search_by_title("", exact_match=False)
        
        # 所有条目都应该包含空字符串
        assert len(result) == len(SAMPLE_ITEMS)
    
    @pytest.mark.unit
    def test_search_error_handling(self, requests_mock):
        """测试搜索错误处理"""
        client = ZoteroLocal()
        
        # Mock get_items 失败
        requests_mock.get(
            f"{client.base_url}/items",
            status_code=500,
            json={"error": "Internal server error"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.search_by_doi("10.1234/test")
    
    @pytest.mark.unit
    def test_search_by_doi_empty_doi_field(self, requests_mock):
        """测试处理空 DOI 字段的条目"""
        client = ZoteroLocal()
        items_with_empty_doi = [
            MockDataFactory.create_item(key="ITEM1", doi=""),
            MockDataFactory.create_item(key="ITEM2", doi="10.1234/test")
        ]
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=items_with_empty_doi,
            status_code=200
        )
        
        result = client.search_by_doi("10.1234/test")
        
        assert len(result) == 1
        assert result[0]["key"] == "ITEM2"
    
    @pytest.mark.unit
    def test_search_by_pmid_multiline_extra(self, requests_mock):
        """测试从多行 extra 字段中搜索 PMID"""
        client = ZoteroLocal()
        items_with_pmid = [
            MockDataFactory.create_item(
                key="ITEM1",
                extra="Line 1\nPMID: 12345\nLine 3"
            ),
            MockDataFactory.create_item(
                key="ITEM2",
                extra="PMID: 67890"
            )
        ]
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=items_with_pmid,
            status_code=200
        )
        
        result = client.search_by_pmid("12345")
        
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"
