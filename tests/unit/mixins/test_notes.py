"""
NotesMixin 单元测试
"""
import pytest
from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError
from tests.fixtures.mock_data import MockDataFactory, SAMPLE_NOTES


class TestNotesMixin:
    """笔记功能测试"""
    
    @pytest.mark.unit
    def test_get_note(self, requests_mock, sample_note_data):
        """测试获取笔记"""
        client = ZoteroLocal()
        note_key = "NOTE123"
        
        requests_mock.get(
            f"{client.base_url}/items/{note_key}",
            json=sample_note_data,
            status_code=200
        )
        
        result = client.get_note(note_key)
        
        assert result == sample_note_data
        assert result["data"]["itemType"] == "note"
        assert result["key"] == note_key
    
    @pytest.mark.unit
    def test_get_note_not_found(self, requests_mock):
        """测试获取不存在的笔记"""
        client = ZoteroLocal()
        note_key = "NOTFOUND"
        
        requests_mock.get(
            f"{client.base_url}/items/{note_key}",
            status_code=404,
            json={"error": "Not Found"}
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.get_note(note_key)
        
        assert "Failed to get note" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_note_wrong_type(self, requests_mock):
        """测试获取非笔记类型的条目"""
        client = ZoteroLocal()
        item_key = "ARTICLE123"
        
        # 返回一个文章类型的条目
        article_item = MockDataFactory.create_item(
            key=item_key,
            item_type="journalArticle"
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}",
            json=article_item,
            status_code=200
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.get_note(item_key)
        
        assert "not a note" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_item_notes(self, requests_mock):
        """测试获取条目的所有笔记"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        # 返回包含笔记和附件的混合列表
        children = [
            SAMPLE_NOTES[0],
            SAMPLE_NOTES[1],
            MockDataFactory.create_attachment(key="ATTACH1", parent_item=item_key)
        ]
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/children",
            json=children,
            status_code=200
        )
        
        result = client.get_item_notes(item_key)
        
        assert isinstance(result, list)
        # 应该只返回笔记，过滤掉附件
        assert len(result) == 2
        for note in result:
            assert note["data"]["itemType"] == "note"
    
    @pytest.mark.unit
    def test_get_item_notes_empty(self, requests_mock):
        """测试获取无笔记的条目"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        # 只返回附件，没有笔记
        children = [
            MockDataFactory.create_attachment(key="ATTACH1", parent_item=item_key)
        ]
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/children",
            json=children,
            status_code=200
        )
        
        result = client.get_item_notes(item_key)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_get_item_notes_error(self, requests_mock):
        """测试获取笔记时的错误处理"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/children",
            status_code=500,
            json={"error": "Internal error"}
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.get_item_notes(item_key)
        
        assert "Failed to get item notes" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_add_item_note(self, requests_mock):
        """测试添加笔记"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        note_text = "<p>This is a test note</p>"
        new_note_key = "NEWNOTE123"
        
        # Mock POST 请求创建笔记
        create_response = {
            "success": {
                "0": new_note_key
            }
        }
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=create_response,
            status_code=201
        )
        
        # Mock GET 请求获取创建的笔记
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
        assert result["data"]["parentItem"] == item_key
        assert result["data"]["note"] == note_text
    
    @pytest.mark.unit
    def test_add_item_note_with_title(self, requests_mock):
        """测试带标题添加笔记"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        note_text = "<p>Note content</p>"
        note_title = "Important Note"
        new_note_key = "NEWNOTE123"
        
        create_response = {
            "success": {
                "0": new_note_key
            }
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
        
        result = client.add_item_note(item_key, note_text, title=note_title)
        
        assert result["key"] == new_note_key
        # 验证请求中包含了 title
        post_request = requests_mock.request_history[0]
        assert post_request.method == "POST"
    
    @pytest.mark.unit
    def test_add_item_note_html_content(self, requests_mock):
        """测试添加 HTML 格式笔记"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        html_note = """
        <p>This is a <strong>formatted</strong> note with:</p>
        <ul>
            <li>List items</li>
            <li>HTML tags</li>
        </ul>
        """
        new_note_key = "NEWNOTE123"
        
        create_response = {
            "success": {
                "0": new_note_key
            }
        }
        
        requests_mock.post(
            f"{client.base_url}/items",
            json=create_response,
            status_code=201
        )
        
        created_note = MockDataFactory.create_note(
            key=new_note_key,
            parent_item=item_key,
            note_content=html_note
        )
        
        requests_mock.get(
            f"{client.base_url}/items/{new_note_key}",
            json=created_note,
            status_code=200
        )
        
        result = client.add_item_note(item_key, html_note)
        
        assert result["data"]["note"] == html_note
    
    @pytest.mark.unit
    def test_add_note_invalid_parent(self, requests_mock):
        """测试父条目不存在时添加笔记"""
        client = ZoteroLocal()
        item_key = "NOTFOUND"
        note_text = "<p>Test note</p>"
        
        # API 返回错误
        requests_mock.post(
            f"{client.base_url}/items",
            status_code=400,
            json={"error": "Parent item not found"}
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.add_item_note(item_key, note_text)
        
        assert "Failed to add note" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_add_note_api_error(self, requests_mock):
        """测试 API 错误处理"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        note_text = "<p>Test</p>"
        
        # API 返回非预期响应
        requests_mock.post(
            f"{client.base_url}/items",
            json={"unexpected": "response"},
            status_code=200
        )
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.add_item_note(item_key, note_text)
        
        assert "Failed to create note" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_add_note_empty_content(self, requests_mock):
        """测试添加空内容笔记"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        note_text = ""
        new_note_key = "NEWNOTE123"
        
        create_response = {
            "success": {
                "0": new_note_key
            }
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
        
        assert result["data"]["note"] == note_text
