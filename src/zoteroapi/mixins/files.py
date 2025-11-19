from typing import Union, BinaryIO
from pathlib import Path
import os
import shutil
import platform
from urllib.parse import unquote
import zipfile
import io
from ..exceptions import ZoteroLocalError

class FilesMixin:
    """文件操作 Mixin 类。

    提供附件文件的下载、复制和管理功能。支持处理压缩文件
    和跨平台的路径操作。

    Note:
        此类不直接使用，而是通过 ZoteroLocal 类使用。
    """

    def get_item_file(self, item_key: str) -> BinaryIO:
        """获取条目的附件文件内容。

        通过条目 key 下载附件文件的二进制内容。支持处理
        Zotero 自动压缩的文件。

        Args:
            item_key: 条目的唯一标识符

        Returns:
            BinaryIO: 文件内容的二进制流对象

        Raises:
            ZoteroLocalError: 当文件下载失败或条目不存在时抛出

        Examples:
            >>> client = ZoteroLocal()
            >>> file_content = client.get_item_file("ABC123")
            >>> with open("paper.pdf", "wb") as f:
            ...     f.write(file_content.read())

        Note:
            如果文件被压缩，会自动解压并返回第一个文件的内容
        """
        response = self._make_request("GET", f"/items/{item_key}/file")
        
        if (response.headers.get('Content-Type') == 'application/zip' and
            response.headers.get('Zotero-File-Compressed') == 'Yes'):
            z = zipfile.ZipFile(io.BytesIO(response.content))
            return io.BytesIO(z.read(z.namelist()[0]))
        
        return io.BytesIO(response.content)
        
    def copy_attachment_to_downloads(self, file_uri: str, download_dir: str = None) -> str:
        """复制附件文件到下载目录。

        将 Zotero 附件文件复制到指定的下载目录。支持跨平台
        路径处理和自动目录创建。

        Args:
            file_uri: 文件的 URI 路径，如 'file:///path/to/file.pdf'
            download_dir: 目标下载目录。如果为 None，则使用系统默认下载目录

        Returns:
            str: 复制后文件的完整路径

        Raises:
            ZoteroLocalError: 当文件复制失败时抛出

        Examples:
            >>> client = ZoteroLocal()
            >>> # 复制到默认下载目录
            >>> dest_path = client.copy_attachment_to_downloads(
            ...     "file:///Users/name/Zotero/storage/ABC123/paper.pdf"
            ... )
            >>> print(f"文件已复制到: {dest_path}")

            >>> # 复制到指定目录
            >>> dest_path = client.copy_attachment_to_downloads(
            ...     "file:///Users/name/Zotero/storage/ABC123/paper.pdf",
            ...     "/path/to/custom/dir"
            ... )

        Note:
            - Windows 路径和 Unix 路径会自动处理
            - 目标目录不存在时会自动创建
            - 文件名保持不变
        """
        try:
            file_path = self._normalize_path(file_uri)
            file_name = os.path.basename(file_path)
            
            if not download_dir:
                download_dir = str(Path.home() / "Downloads")
                
            os.makedirs(download_dir, exist_ok=True)
            dest_path = os.path.join(download_dir, file_name)
            
            shutil.copy2(file_path, dest_path)
            return dest_path
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to copy file: {str(e)}")
            
    def _normalize_path(self, file_uri: str) -> str:
        """将文件 URI 标准化为系统路径。

        处理不同操作系统的文件 URI 格式，转换为有效的本地路径。

        Args:
            file_uri: 文件 URI，如 'file:///path/to/file.pdf' 或 'file://C:/path/to/file.pdf'

        Returns:
            str: 标准化的本地文件路径

        Note:
            - Windows 系统会去掉开头的 'file:///'
            - Unix 系统会去掉开头的 'file://'
            - 自动处理 URL 编码字符
        """
        if platform.system() == 'Windows':
            path = file_uri.replace('file:///', '')
        else:
            path = file_uri.replace('file://', '')
        
        path = unquote(path)
        return str(Path(path)) 