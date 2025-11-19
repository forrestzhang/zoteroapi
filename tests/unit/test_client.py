"""
ZoteroLocal 主客户端单元测试
"""
import pytest
from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError
from tests.fixtures.mock_data import MockDataFactory, SAMPLE_ITEMS, SAMPLE_COLLECTIONS


class TestZoteroLocalInit:
    """客户端初始化测试"""
    
    @pytest.mark.unit
    def test_client_initialization(self):
        """测试客户端初始化 - 使用默认 URL"""
        client = ZoteroLocal()
        assert client.base_url == "http://localhost:23119/api/users/000000"
    
    @pytest.mark.unit
    def test_client_initialization_custom_url(self):
        """测试客户端初始化 - 使用自定义 URL"""
        custom_url = "http://localhost:23119/api/users/123456/"
        client = ZoteroLocal(custom_url)
        assert client.base_url == "http://localhost:23119/api/users/123456"


class TestItemOperations:
    """条目操作测试"""
    
    @pytest.mark.unit
    def test_get_item(self, requests_mock, sample_item_data):
        """测试获取单个条目"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=sample_item_data,
            status_code=200
        )
        
        result = client.get_item(item_key)
        
        assert result == sample_item_data
        assert result["key"] == item_key
        assert result["data"]["title"] == "Sample Research Article"
    
    @pytest.mark.unit
    def test_get_item_not_found(self, requests_mock):
        """测试获取不存在的条目"""
        client = ZoteroLocal()
        item_key = "NOTFOUND"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            status_code=404,
            json={"error": "Not Found"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.get_item(item_key)
    
    @pytest.mark.unit
    def test_get_items(self, requests_mock):
        """测试获取所有条目"""
        client = ZoteroLocal()
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS,
            status_code=200
        )
        
        result = client.get_items()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["key"] == "ITEM001"
    
    @pytest.mark.unit
    def test_get_items_with_limit(self, requests_mock):
        """测试带限制参数获取条目"""
        client = ZoteroLocal()
        limit = 10
        
        requests_mock.get(
            f"{client.base_url}/items",
            json=SAMPLE_ITEMS[:2],
            status_code=200
        )
        
        result = client.get_items(limit=limit)
        
        assert isinstance(result, list)
        # 验证请求包含 limit 参数
        assert f"limit={limit}" in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_get_items_top(self, requests_mock):
        """测试获取顶层条目"""
        client = ZoteroLocal()
        top_items = [SAMPLE_ITEMS[0], SAMPLE_ITEMS[1]]
        
        requests_mock.get(
            f"{client.base_url}/items/top",
            json=top_items,
            status_code=200
        )
        
        result = client.get_items_top(limit=10)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "limit=10" in requests_mock.last_request.url
    
    @pytest.mark.unit
    def test_get_item_by_key(self, requests_mock, sample_item_data):
        """测试通过 key 获取条目"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=sample_item_data,
            status_code=200
        )
        
        result = client.get_item_by_key(item_key)
        
        assert result == sample_item_data
        assert result["key"] == item_key


class TestCollectionOperations:
    """文献集操作测试"""
    
    @pytest.mark.unit
    def test_get_collections(self, requests_mock):
        """测试获取所有文献集"""
        client = ZoteroLocal()
        
        requests_mock.get(
            f"{client.base_url}/collections",
            json=SAMPLE_COLLECTIONS,
            status_code=200
        )
        
        result = client.get_collections()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["key"] == "COLL001"
        assert result[0]["data"]["name"] == "Programming"
    
    @pytest.mark.unit
    def test_get_collection(self, requests_mock, sample_collection_data):
        """测试获取单个文献集"""
        client = ZoteroLocal()
        coll_key = "COLL123"
        
        requests_mock.get(
            f"{client.base_url}/collections/{coll_key}",
            json=sample_collection_data,
            status_code=200
        )
        
        result = client.get_collection(coll_key)
        
        assert result == sample_collection_data
        assert result["key"] == coll_key
        assert result["data"]["name"] == "Test Collection"
    
    @pytest.mark.unit
    def test_get_collection_items(self, requests_mock):
        """测试获取文献集中的条目"""
        client = ZoteroLocal()
        coll_key = "COLL001"
        collection_items = [SAMPLE_ITEMS[0]]
        
        requests_mock.get(
            f"{client.base_url}/collections/{coll_key}/items",
            json=collection_items,
            status_code=200
        )
        
        result = client.get_collection_items(coll_key)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "ITEM001"
    
    @pytest.mark.unit
    def test_get_collection_not_found(self, requests_mock):
        """测试获取不存在的文献集"""
        client = ZoteroLocal()
        coll_key = "NOTFOUND"
        
        requests_mock.get(
            f"{client.base_url}/collections/{coll_key}",
            status_code=404,
            json={"error": "Collection not found"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.get_collection(coll_key)


class TestTagsAndMetadata:
    """标签和元数据测试"""
    
    @pytest.mark.unit
    def test_get_tags(self, requests_mock):
        """测试获取所有标签"""
        client = ZoteroLocal()
        tags = [
            {"tag": "python"},
            {"tag": "testing"},
            {"tag": "research"}
        ]
        
        requests_mock.get(
            f"{client.base_url}/tags",
            json=tags,
            status_code=200
        )
        
        result = client.get_tags()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["tag"] == "python"
    
    @pytest.mark.unit
    def test_get_pmid(self, requests_mock):
        """测试从条目中提取 PMID"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        item_with_pmid = MockDataFactory.create_item(
            key=item_key,
            pmid="12345678"
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_with_pmid,
            status_code=200
        )
        
        result = client.get_pmid(item_key)
        
        assert result == "12345678"
    
    @pytest.mark.unit
    def test_get_pmid_not_found(self, requests_mock):
        """测试 PMID 不存在的情况"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        item_without_pmid = MockDataFactory.create_item(
            key=item_key,
            extra=""
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_without_pmid,
            status_code=200
        )
        
        result = client.get_pmid(item_key)
        
        assert result == ""
    
    @pytest.mark.unit
    def test_get_pmid_multiline_extra(self, requests_mock):
        """测试从多行 extra 字段中提取 PMID"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        item_data = MockDataFactory.create_item(
            key=item_key,
            extra="Some other info\nPMID: 98765432\nMore info"
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_data,
            status_code=200
        )
        
        result = client.get_pmid(item_key)
        
        assert result == "98765432"


class TestAttachmentOperations:
    """附件操作测试"""
    
    @pytest.mark.unit
    def test_get_item_file(self, requests_mock):
        """测试获取附件文件"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        file_content = b"PDF file content"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            content=file_content,
            headers={"Content-Type": "application/pdf"},
            status_code=200
        )
        
        result = client.get_item_file(item_key)
        
        import io
        assert isinstance(result, io.BytesIO)
        assert result.read() == file_content
    
    @pytest.mark.unit
    def test_get_item_attachment_href(self, requests_mock):
        """测试获取附件下载链接"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        attachment_href = "http://localhost:23119/api/users/000000/items/ATTACH123"
        download_href = "http://localhost:23119/api/users/000000/items/ATTACH123/file"
        
        # Mock get_item_by_key 返回的条目数据
        item_with_attachment = {
            "key": item_key,
            "links": {
                "attachment": {
                    "href": attachment_href,
                    "attachmentType": "application/pdf"
                }
            }
        }
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_with_attachment,
            status_code=200
        )
        
        # Mock 附件详情请求
        attachment_details = {
            "links": {
                "enclosure": {
                    "href": download_href
                }
            }
        }
        
        requests_mock.get(
            attachment_href,
            json=attachment_details,
            status_code=200
        )
        
        result = client.get_item_attachment_href(item_key)
        
        assert result == download_href
    
    @pytest.mark.unit
    def test_get_item_attachment_no_pdf(self, requests_mock):
        """测试非 PDF 附件"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        item_data = {
            "key": item_key,
            "links": {
                "attachment": {
                    "href": "http://example.com/attachment",
                    "attachmentType": "text/html"  # 非 PDF
                }
            }
        }
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=item_data,
            status_code=200
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.get_item_attachment_href(item_key)
        
        assert "not PDF" in str(exc_info.value) or "不是PDF" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_download_file(self, requests_mock, temp_download_dir):
        """测试下载文件到本地"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        file_content = b"Test PDF content"
        download_path = temp_download_dir / "test.pdf"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            content=file_content,
            status_code=200
        )
        
        client.download_file(item_key, str(download_path))
        
        assert download_path.exists()
        assert download_path.read_bytes() == file_content
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_download_file_create_dir(self, requests_mock, temp_download_dir):
        """测试下载时创建目录"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        file_content = b"Test content"
        nested_path = temp_download_dir / "nested" / "dir" / "file.pdf"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            content=file_content,
            status_code=200
        )
        
        client.download_file(item_key, str(nested_path))
        
        assert nested_path.exists()
        assert nested_path.parent.exists()
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_upload_file(self, requests_mock, temp_test_file):
        """测试上传文件"""
        client = ZoteroLocal()
        new_item_key = "NEWFILE123"
        
        # Mock 创建附件条目
        create_response = {
            "successful": [{"key": new_item_key}]
        }
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=create_response,
            status_code=201
        )
        
        # Mock 上传文件内容
        requests_mock.post(
            f"{client.base_url}/items/{new_item_key}/file",
            json={"success": True},
            status_code=200
        )
        
        # Mock 获取上传后的条目
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
    
    @pytest.mark.unit
    def test_upload_file_not_found(self):
        """测试上传不存在的文件"""
        client = ZoteroLocal()
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.upload_file("/nonexistent/file.pdf")
        
        assert "不存在" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_upload_file_with_parent(self, requests_mock, temp_test_file):
        """测试带父条目上传"""
        client = ZoteroLocal()
        parent_key = "PARENT123"
        new_item_key = "NEWFILE123"
        
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
            parent_item=parent_key,
            filename=temp_test_file.name
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{new_item_key}",
            json=uploaded_item,
            status_code=200
        )
        
        result = client.upload_file(str(temp_test_file), parent_item=parent_key)
        
        assert result["data"]["parentItem"] == parent_key


class TestUtilityMethods:
    """工具方法测试"""
    
    @pytest.mark.unit
    def test_guess_mimetype(self):
        """测试 MIME 类型推断"""
        from pathlib import Path
        client = ZoteroLocal()
        
        # PDF 文件
        assert "pdf" in client._guess_mimetype(Path("test.pdf")).lower()
        
        # 文本文件
        assert "text" in client._guess_mimetype(Path("test.txt")).lower()
        
        # HTML 文件
        assert "html" in client._guess_mimetype(Path("test.html")).lower()
    
    @pytest.mark.unit
    def test_guess_mimetype_unknown(self):
        """测试未知类型处理"""
        from pathlib import Path
        client = ZoteroLocal()
        
        result = client._guess_mimetype(Path("test.unknownext"))
        
        assert result == "application/octet-stream"
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_calculate_md5(self, temp_test_file):
        """测试 MD5 计算"""
        client = ZoteroLocal()
        
        result = client._calculate_md5(temp_test_file)
        
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 哈希长度
        # 验证是十六进制字符串
        assert all(c in '0123456789abcdef' for c in result.lower())
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_calculate_md5_consistency(self, temp_test_file):
        """测试 MD5 计算一致性"""
        client = ZoteroLocal()
        
        result1 = client._calculate_md5(temp_test_file)
        result2 = client._calculate_md5(temp_test_file)
        
        assert result1 == result2
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_copy_attachment_to_downloads(self, temp_test_file, temp_download_dir):
        """测试复制附件到下载目录"""
        import platform
        client = ZoteroLocal()
        
        if platform.system() == 'Windows':
            file_uri = f"file:///{temp_test_file}"
        else:
            file_uri = f"file://{temp_test_file}"
        
        result = client.copy_attachment_to_downloads(file_uri, str(temp_download_dir))
        
        from pathlib import Path
        assert Path(result).exists()
        assert temp_test_file.name in result
