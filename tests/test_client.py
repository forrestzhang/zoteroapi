import pytest
from zotero_local_api import ZoteroLocal, ZoteroLocalError

def test_client_initialization():
    client = ZoteroLocal()
    assert client.base_url == "http://localhost:23119/api"
    
    client = ZoteroLocal("http://localhost:23119/api/")
    assert client.base_url == "http://localhost:23119/api" 