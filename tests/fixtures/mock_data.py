"""
Mock 数据工厂 - 提供测试用的模拟数据
"""
from typing import Dict, Any


class MockDataFactory:
    """Mock 数据工厂类"""
    
    @staticmethod
    def create_item(
        key: str = "TESTITEM",
        item_type: str = "journalArticle",
        title: str = "Test Article",
        doi: str = None,
        pmid: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建一个模拟的条目数据"""
        extra = kwargs.get("extra", "")
        if pmid and "PMID:" not in extra:
            extra = f"PMID: {pmid}\n{extra}".strip()
        
        return {
            "key": key,
            "version": kwargs.get("version", 1),
            "library": {
                "type": "user",
                "id": 000000,
                "name": "test_user"
            },
            "data": {
                "key": key,
                "version": kwargs.get("version", 1),
                "itemType": item_type,
                "title": title,
                "creators": kwargs.get("creators", []),
                "DOI": doi or "",
                "extra": extra,
                "tags": kwargs.get("tags", []),
                "collections": kwargs.get("collections", []),
                "relations": {},
                "dateAdded": "2023-01-01T00:00:00Z",
                "dateModified": "2023-01-01T00:00:00Z"
            },
            "links": kwargs.get("links", {})
        }
    
    @staticmethod
    def create_collection(
        key: str = "TESTCOLL",
        name: str = "Test Collection",
        parent: str = None
    ) -> Dict[str, Any]:
        """创建一个模拟的文献集数据"""
        return {
            "key": key,
            "version": 1,
            "library": {
                "type": "user",
                "id": 000000,
                "name": "test_user"
            },
            "data": {
                "key": key,
                "version": 1,
                "name": name,
                "parentCollection": parent or False,
                "relations": {}
            }
        }
    
    @staticmethod
    def create_note(
        key: str = "TESTNOTE",
        parent_item: str = "TESTITEM",
        note_content: str = "<p>Test note</p>",
        **kwargs
    ) -> Dict[str, Any]:
        """创建一个模拟的笔记数据"""
        return {
            "key": key,
            "version": kwargs.get("version", 1),
            "library": {
                "type": "user",
                "id": 000000,
                "name": "test_user"
            },
            "data": {
                "key": key,
                "version": kwargs.get("version", 1),
                "itemType": "note",
                "parentItem": parent_item,
                "note": note_content,
                "tags": kwargs.get("tags", []),
                "collections": kwargs.get("collections", []),
                "relations": {},
                "dateAdded": "2023-01-01T00:00:00Z",
                "dateModified": "2023-01-01T00:00:00Z"
            }
        }
    
    @staticmethod
    def create_attachment(
        key: str = "TESTATTACH",
        parent_item: str = "TESTITEM",
        filename: str = "test.pdf",
        content_type: str = "application/pdf"
    ) -> Dict[str, Any]:
        """创建一个模拟的附件数据"""
        return {
            "key": key,
            "version": 1,
            "library": {
                "type": "user",
                "id": 000000,
                "name": "test_user"
            },
            "data": {
                "key": key,
                "version": 1,
                "itemType": "attachment",
                "parentItem": parent_item,
                "linkMode": "imported_file",
                "title": filename,
                "accessDate": "",
                "url": "",
                "note": "",
                "contentType": content_type,
                "charset": "",
                "filename": filename,
                "tags": [],
                "relations": {},
                "dateAdded": "2023-01-01T00:00:00Z",
                "dateModified": "2023-01-01T00:00:00Z"
            }
        }


# 预定义的测试数据集
SAMPLE_ITEMS = [
    MockDataFactory.create_item(
        key="ITEM001",
        title="Python Programming",
        doi="10.1234/python.001",
        pmid="11111111"
    ),
    MockDataFactory.create_item(
        key="ITEM002",
        title="Machine Learning Basics",
        doi="10.1234/ml.002",
        pmid="22222222"
    ),
    MockDataFactory.create_item(
        key="ITEM003",
        title="Deep Learning Advanced",
        doi="10.1234/dl.003"
    )
]

SAMPLE_COLLECTIONS = [
    MockDataFactory.create_collection(key="COLL001", name="Programming"),
    MockDataFactory.create_collection(key="COLL002", name="AI Research"),
    MockDataFactory.create_collection(key="COLL003", name="Data Science")
]

SAMPLE_NOTES = [
    MockDataFactory.create_note(
        key="NOTE001",
        parent_item="ITEM001",
        note_content="<p>Important findings about <strong>Python</strong></p>"
    ),
    MockDataFactory.create_note(
        key="NOTE002",
        parent_item="ITEM002",
        note_content="<p>Summary of ML concepts</p>"
    )
]
