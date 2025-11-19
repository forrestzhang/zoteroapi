"""
工作流集成测试
"""
import pytest
from zoteroapi import ZoteroLocal
from tests.fixtures.mock_data import MockDataFactory, SAMPLE_ITEMS, SAMPLE_NOTES


class TestWorkflows:
    """端到端工作流测试"""
    
    @pytest.mark.integration
    def test_search_and_get_note_workflow(self, requests_mock):
        """测试搜索条目并获取笔记的完整流程"""
        client = ZoteroLocal()
        
        # Step 1: 搜索条目
        search_query = "python"
        search_results = [SAMPLE_ITEMS[0]]
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=search_results,
            status_code=200
        )
        
        items = client.search_items(search_query)
        assert len(items) == 1
        
        # Step 2: 获取条目的笔记
        item_key = items[0]["key"]
        notes = [SAMPLE_NOTES[0]]
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/children",
            json=notes,
            status_code=200
        )
        
        item_notes = client.get_item_notes(item_key)
        
        # Step 3: 验证笔记内容
        assert len(item_notes) == 1
        assert item_notes[0]["data"]["itemType"] == "note"
        assert "Python" in item_notes[0]["data"]["note"]
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_upload_and_download_workflow(self, requests_mock, temp_test_file, temp_download_dir):
        """测试上传下载附件的完整流程"""
        client = ZoteroLocal()
        new_item_key = "NEWFILE123"
        
        # Step 1: 上传文件
        create_response = {
            "successful": [{"key": new_item_key}]
        }
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=create_response,
            status_code=201
        )
        
        requests_mock.post(
            f"{client.base_url}/items/{new_item_key}/file",
            json={"success": True},
            status_code=200
        )
        
        uploaded_item = MockDataFactory.create_attachment(
            key=new_item_key,
            filename=temp_test_file.name
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{new_item_key}",
            json=uploaded_item,
            status_code=200
        )
        
        result = client.upload_file(str(temp_test_file))
        assert result["key"] == new_item_key
        
        # Step 2: 下载文件
        original_content = temp_test_file.read_bytes()
        
        requests_mock.get(
            f"{client.base_url}/items/{new_item_key}/file",
            content=original_content,
            status_code=200
        )
        
        download_path = temp_download_dir / "downloaded.txt"
        client.download_file(new_item_key, str(download_path))
        
        # Step 3: 验证内容一致
        assert download_path.exists()
        assert download_path.read_bytes() == original_content
    
    @pytest.mark.integration
    def test_add_note_and_retrieve_workflow(self, requests_mock):
        """测试添加笔记并检索的完整流程"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        note_text = "<p>Integration test note</p>"
        new_note_key = "NEWNOTE123"
        
        # Step 1: 创建笔记
        create_response = {
            "success": {"0": new_note_key}
        }
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=create_response,
            status_code=201
        )
        
        created_note = MockDataFactory.create_note(
            key=new_note_key,
            parent_item=item_key,
            note_content=note_text
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{new_note_key}",
            json=created_note,
            status_code=200
        )
        
        result = client.add_item_note(item_key, note_text)
        assert result["key"] == new_note_key
        
        # Step 2: 通过条目获取笔记
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/children",
            json=[created_note],
            status_code=200
        )
        
        notes = client.get_item_notes(item_key)
        
        # Step 3: 验证笔记存在
        assert len(notes) == 1
        assert notes[0]["key"] == new_note_key
        assert notes[0]["data"]["note"] == note_text
    
    @pytest.mark.integration
    def test_collection_items_workflow(self, requests_mock):
        """测试文献集操作的完整流程"""
        client = ZoteroLocal()
        
        # Step 1: 获取所有文献集
        from tests.fixtures.mock_data import SAMPLE_COLLECTIONS
        
        requests_mock.get(
            f"{client.base_url}/collections",
            json=SAMPLE_COLLECTIONS,
            status_code=200
        )
        
        collections = client.get_collections()
        assert len(collections) > 0
        
        # Step 2: 获取特定文献集的条目
        coll_key = collections[0]["key"]
        collection_items = [SAMPLE_ITEMS[0]]
        
        requests_mock.get(
            f"{client.base_url}/collections/{coll_key}/items",
            json=collection_items,
            status_code=200
        )
        
        items = client.get_collection_items(coll_key)
        assert len(items) == 1
        
        # Step 3: 搜索特定条目
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        search_results = client.search_by_title("Python")
        assert len(search_results) > 0
    
    @pytest.mark.integration
    def test_multi_search_workflow(self, requests_mock):
        """测试多种搜索方式组合的流程"""
        client = ZoteroLocal()
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        # Step 1: 通过标题搜索
        title_results = client.search_by_title("Python")
        assert len(title_results) > 0
        
        # Step 2: 通过 DOI 搜索
        doi_results = client.search_by_doi("10.1234/python.001")
        assert len(doi_results) == 1
        
        # Step 3: 通过 PMID 搜索
        pmid_results = client.search_by_pmid("11111111")
        assert len(pmid_results) == 1
        
        # Step 4: 验证结果一致性
        assert title_results[0]["key"] == doi_results[0]["key"]
        assert doi_results[0]["key"] == pmid_results[0]["key"]
    
    @pytest.mark.integration
    def test_item_metadata_workflow(self, requests_mock):
        """测试条目元数据提取工作流"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        # 创建包含完整元数据的条目
        item_with_metadata = MockDataFactory.create_item(
            key=item_key,
            title="Test Article",
            doi="10.1234/test.001",
            pmid="12345678"
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_with_metadata,
            status_code=200
        )
        
        # Step 1: 获取条目
        item = client.get_item(item_key)
        assert item["data"]["title"] == "Test Article"
        
        # Step 2: 提取 PMID
        pmid = client.get_pmid(item_key)
        assert pmid == "12345678"
        
        # Step 3: 提取 DOI
        doi = item["data"]["DOI"]
        assert doi == "10.1234/test.001"
