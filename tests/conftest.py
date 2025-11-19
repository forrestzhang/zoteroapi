"""
pytest 全局配置和共享 fixtures
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def base_client():
    """返回 BaseZoteroClient 实例"""
    from zoteroapi.base_client import BaseZoteroClient
    return BaseZoteroClient()


@pytest.fixture
def mock_client(requests_mock):
    """返回配置好的 Mock ZoteroLocal 客户端实例"""
    from zoteroapi import ZoteroLocal
    client = ZoteroLocal()
    return client


@pytest.fixture
def sample_item_data() -> Dict[str, Any]:
    """提供样本条目数据字典"""
    return {
        "key": "ITEM123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 000000,
            "name": "test_user"
        },
        "data": {
            "key": "ITEM123",
            "version": 1,
            "itemType": "journalArticle",
            "title": "Sample Research Article",
            "creators": [
                {
                    "creatorType": "author",
                    "firstName": "John",
                    "lastName": "Doe"
                }
            ],
            "abstractNote": "This is a sample abstract",
            "publicationTitle": "Journal of Examples",
            "volume": "42",
            "issue": "1",
            "pages": "1-10",
            "date": "2023",
            "DOI": "10.1234/example.2023.001",
            "extra": "PMID: 12345678",
            "tags": [
                {"tag": "example"},
                {"tag": "test"}
            ],
            "collections": ["COLL123"],
            "relations": {},
            "dateAdded": "2023-01-01T00:00:00Z",
            "dateModified": "2023-01-01T00:00:00Z"
        },
        "links": {
            "self": {
                "href": "http://localhost:23119/api/users/000000/items/ITEM123",
                "type": "application/json"
            },
            "attachment": {
                "href": "http://localhost:23119/api/users/000000/items/ATTACH123",
                "attachmentType": "application/pdf",
                "attachmentSize": 102400
            }
        }
    }


@pytest.fixture
def sample_collection_data() -> Dict[str, Any]:
    """提供样本文献集数据"""
    return {
        "key": "COLL123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 000000,
            "name": "test_user"
        },
        "data": {
            "key": "COLL123",
            "version": 1,
            "name": "Test Collection",
            "parentCollection": False,
            "relations": {}
        },
        "links": {
            "self": {
                "href": "http://localhost:23119/api/users/000000/collections/COLL123",
                "type": "application/json"
            }
        }
    }


@pytest.fixture
def sample_note_data() -> Dict[str, Any]:
    """提供样本笔记数据"""
    return {
        "key": "NOTE123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 000000,
            "name": "test_user"
        },
        "data": {
            "key": "NOTE123",
            "version": 1,
            "itemType": "note",
            "parentItem": "ITEM123",
            "note": "<p>This is a <strong>sample note</strong> with HTML formatting.</p>",
            "tags": [
                {"tag": "important"}
            ],
            "collections": [],
            "relations": {},
            "dateAdded": "2023-01-01T00:00:00Z",
            "dateModified": "2023-01-01T00:00:00Z"
        },
        "links": {
            "self": {
                "href": "http://localhost:23119/api/users/000000/items/NOTE123",
                "type": "application/json"
            }
        }
    }


@pytest.fixture
def temp_test_file():
    """创建临时测试文件，测试后自动清理"""
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test_file.txt"
    test_file.write_text("This is a test file content")
    
    yield test_file
    
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_pdf_file():
    """创建临时 PDF 测试文件"""
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test_file.pdf"
    # 创建一个简单的 PDF 文件标识符
    test_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    
    yield test_file
    
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_download_dir():
    """创建临时下载目录，测试后自动清理"""
    temp_dir = tempfile.mkdtemp()
    download_dir = Path(temp_dir)
    
    yield download_dir
    
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def mock_api_responses() -> Dict[str, Any]:
    """预定义的 API 响应数据集合"""
    return {
        "items_list": [
            {
                "key": "ITEM001",
                "version": 1,
                "data": {
                    "itemType": "journalArticle",
                    "title": "First Article",
                    "DOI": "10.1234/first"
                }
            },
            {
                "key": "ITEM002",
                "version": 1,
                "data": {
                    "itemType": "book",
                    "title": "Second Book",
                    "DOI": "10.1234/second"
                }
            }
        ],
        "collections_list": [
            {
                "key": "COLL001",
                "version": 1,
                "data": {
                    "name": "Collection One"
                }
            },
            {
                "key": "COLL002",
                "version": 1,
                "data": {
                    "name": "Collection Two"
                }
            }
        ],
        "tags_list": [
            {"tag": "python"},
            {"tag": "testing"},
            {"tag": "automation"}
        ],
        "error_404": {
            "error": "Not Found",
            "message": "The requested resource was not found"
        },
        "error_500": {
            "error": "Internal Server Error",
            "message": "An internal error occurred"
        }
    }
