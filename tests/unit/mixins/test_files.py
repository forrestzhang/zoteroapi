"""
FilesMixin 单元测试
"""
import pytest
import io
import zipfile
import platform
from pathlib import Path
from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError


class TestFilesMixin:
    """文件操作测试"""
    
    @pytest.mark.unit
    def test_get_item_file_normal(self, requests_mock):
        """测试获取普通文件"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        file_content = b"This is a PDF file content"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            content=file_content,
            headers={"Content-Type": "application/pdf"},
            status_code=200
        )
        
        result = client.get_item_file(item_key)
        
        assert isinstance(result, io.BytesIO)
        assert result.read() == file_content
    
    @pytest.mark.unit
    def test_get_item_file_compressed(self, requests_mock):
        """测试获取压缩文件并自动解压"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        original_content = b"Original file content"
        
        # 创建一个 zip 文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("file.pdf", original_content)
        zip_content = zip_buffer.getvalue()
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            content=zip_content,
            headers={
                "Content-Type": "application/zip",
                "Zotero-File-Compressed": "Yes"
            },
            status_code=200
        )
        
        result = client.get_item_file(item_key)
        
        assert isinstance(result, io.BytesIO)
        assert result.read() == original_content
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_copy_attachment_to_downloads(self, temp_test_file, temp_download_dir):
        """测试复制附件到下载目录"""
        client = ZoteroLocal()
        
        # 使用 file:// URI 格式
        if platform.system() == 'Windows':
            file_uri = f"file:///{temp_test_file}"
        else:
            file_uri = f"file://{temp_test_file}"
        
        result = client.copy_attachment_to_downloads(file_uri, str(temp_download_dir))
        
        assert Path(result).exists()
        assert Path(result).parent == temp_download_dir
        assert Path(result).name == temp_test_file.name
        # 验证内容相同
        assert Path(result).read_text() == temp_test_file.read_text()
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_copy_attachment_custom_dir(self, temp_test_file, temp_download_dir):
        """测试复制到自定义目录"""
        client = ZoteroLocal()
        custom_dir = temp_download_dir / "custom"
        
        if platform.system() == 'Windows':
            file_uri = f"file:///{temp_test_file}"
        else:
            file_uri = f"file://{temp_test_file}"
        
        result = client.copy_attachment_to_downloads(file_uri, str(custom_dir))
        
        assert Path(result).exists()
        assert Path(result).parent == custom_dir
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_copy_attachment_create_dir(self, temp_test_file, temp_download_dir):
        """测试目标目录不存在时自动创建"""
        client = ZoteroLocal()
        nested_dir = temp_download_dir / "nested" / "dir"
        
        if platform.system() == 'Windows':
            file_uri = f"file:///{temp_test_file}"
        else:
            file_uri = f"file://{temp_test_file}"
        
        result = client.copy_attachment_to_downloads(file_uri, str(nested_dir))
        
        assert nested_dir.exists()
        assert Path(result).exists()
    
    @pytest.mark.unit
    def test_normalize_path_unix(self):
        """测试 Unix 路径规范化"""
        client = ZoteroLocal()
        
        if platform.system() != 'Windows':
            file_uri = "file:///home/user/documents/test.pdf"
            result = client._normalize_path(file_uri)
            
            assert result == "/home/user/documents/test.pdf"
    
    @pytest.mark.unit
    def test_normalize_path_windows(self):
        """测试 Windows 路径规范化"""
        client = ZoteroLocal()
        
        if platform.system() == 'Windows':
            file_uri = "file:///C:/Users/test/Documents/test.pdf"
            result = client._normalize_path(file_uri)
            
            assert "C:" in result or "c:" in result
            assert "test.pdf" in result
    
    @pytest.mark.unit
    def test_normalize_path_url_encoded(self):
        """测试 URL 编码路径的正确解码"""
        client = ZoteroLocal()
        
        # URL 编码的空格和特殊字符
        if platform.system() == 'Windows':
            file_uri = "file:///C:/Users/test/My%20Documents/test%20file.pdf"
        else:
            file_uri = "file:///home/user/My%20Documents/test%20file.pdf"
        
        result = client._normalize_path(file_uri)
        
        assert "My Documents" in result
        assert "test file.pdf" in result
        assert "%20" not in result
    
    @pytest.mark.unit
    def test_copy_file_error(self, temp_download_dir):
        """测试复制不存在的文件"""
        client = ZoteroLocal()
        
        if platform.system() == 'Windows':
            file_uri = "file:///C:/nonexistent/file.pdf"
        else:
            file_uri = "file:///nonexistent/file.pdf"
        
        with pytest.raises(ZoteroLocalError) as exc_info:
            client.copy_attachment_to_downloads(file_uri, str(temp_download_dir))
        
        assert "Failed to copy file" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_normalize_path_special_characters(self):
        """测试包含特殊字符的路径"""
        client = ZoteroLocal()
        
        if platform.system() == 'Windows':
            file_uri = "file:///C:/Users/test/%E4%B8%AD%E6%96%87/file.pdf"
        else:
            file_uri = "file:///home/user/%E4%B8%AD%E6%96%87/file.pdf"
        
        result = client._normalize_path(file_uri)
        
        # URL 解码后应该包含中文字符
        assert "中文" in result
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_copy_attachment_default_download_dir(self, temp_test_file, monkeypatch):
        """测试使用默认下载目录"""
        import tempfile
        client = ZoteroLocal()
        
        # 创建临时目录作为默认下载目录
        temp_home = Path(tempfile.mkdtemp())
        temp_downloads = temp_home / "Downloads"
        temp_downloads.mkdir(exist_ok=True)
        
        # Mock Path.home() 返回临时目录
        monkeypatch.setattr(Path, "home", lambda: temp_home)
        
        if platform.system() == 'Windows':
            file_uri = f"file:///{temp_test_file}"
        else:
            file_uri = f"file://{temp_test_file}"
        
        result = client.copy_attachment_to_downloads(file_uri)
        
        assert Path(result).exists()
        assert "Downloads" in result
        
        # 清理
        import shutil
        shutil.rmtree(temp_home, ignore_errors=True)
    
    @pytest.mark.unit
    def test_get_item_file_error(self, requests_mock):
        """测试获取文件时的错误"""
        client = ZoteroLocal()
        item_key = "ITEM123"
        
        requests_mock.get(
            f"{client.base_url}/items/{item_key}/file",
            status_code=404,
            json={"error": "File not found"}
        )
        
        with pytest.raises(ZoteroLocalError):
            client.get_item_file(item_key)
