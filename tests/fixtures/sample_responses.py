"""
模拟 API 响应数据 - 基于真实 Zotero API 响应格式
"""


# 成功的 API 响应
SUCCESSFUL_ITEM_RESPONSE = {
    "key": "ABC123XYZ",
    "version": 42,
    "library": {
        "type": "user",
        "id": 000000,
        "name": "testuser",
        "links": {
            "alternate": {
                "href": "https://www.zotero.org/testuser",
                "type": "text/html"
            }
        }
    },
    "links": {
        "self": {
            "href": "http://localhost:23119/api/users/000000/items/ABC123XYZ",
            "type": "application/json"
        },
        "alternate": {
            "href": "https://www.zotero.org/testuser/items/ABC123XYZ",
            "type": "text/html"
        }
    },
    "meta": {
        "createdByUser": {
            "id": 000000,
            "username": "testuser",
            "name": "Test User"
        },
        "creatorSummary": "Doe et al.",
        "parsedDate": "2023",
        "numChildren": 2
    },
    "data": {
        "key": "ABC123XYZ",
        "version": 42,
        "itemType": "journalArticle",
        "title": "Example Research Article Title",
        "creators": [
            {
                "creatorType": "author",
                "firstName": "John",
                "lastName": "Doe"
            },
            {
                "creatorType": "author",
                "firstName": "Jane",
                "lastName": "Smith"
            }
        ],
        "abstractNote": "This is an example abstract of the research article.",
        "publicationTitle": "Nature",
        "volume": "500",
        "issue": "7463",
        "pages": "123-456",
        "date": "2023-08-15",
        "series": "",
        "seriesTitle": "",
        "seriesText": "",
        "journalAbbreviation": "Nature",
        "language": "en",
        "DOI": "10.1038/nature12345",
        "ISSN": "0028-0836",
        "shortTitle": "",
        "url": "https://doi.org/10.1038/nature12345",
        "accessDate": "2023-09-01T12:00:00Z",
        "archive": "",
        "archiveLocation": "",
        "libraryCatalog": "",
        "callNumber": "",
        "rights": "",
        "extra": "PMID: 23456789",
        "tags": [
            {"tag": "research"},
            {"tag": "biology"},
            {"tag": "genetics"}
        ],
        "collections": ["COLL123ABC"],
        "relations": {},
        "dateAdded": "2023-08-01T10:30:00Z",
        "dateModified": "2023-08-15T14:45:00Z"
    }
}


# 文件上传成功响应
FILE_UPLOAD_SUCCESS_RESPONSE = {
    "successful": [
        {
            "key": "NEWFILE123",
            "version": 1,
            "data": {
                "key": "NEWFILE123",
                "version": 1,
                "itemType": "attachment",
                "linkMode": "imported_file",
                "title": "uploaded_file.pdf",
                "contentType": "application/pdf",
                "filename": "uploaded_file.pdf"
            }
        }
    ],
    "unchanged": [],
    "failed": []
}


# 笔记创建成功响应
NOTE_CREATE_SUCCESS_RESPONSE = {
    "success": {
        "0": "NEWNOTE123"
    },
    "successful": {
        "0": {
            "key": "NEWNOTE123",
            "version": 1,
            "data": {
                "key": "NEWNOTE123",
                "version": 1,
                "itemType": "note",
                "note": "<p>Test note content</p>",
                "parentItem": "PARENT123"
            }
        }
    },
    "unchanged": {},
    "failed": {}
}


# 错误响应
ERROR_RESPONSES = {
    "404": {
        "message": "Item not found",
        "code": 404
    },
    "400": {
        "message": "Invalid request",
        "code": 400
    },
    "500": {
        "message": "Internal server error",
        "code": 500
    }
}
