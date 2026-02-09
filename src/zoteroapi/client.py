import requests
import os
import zipfile
import io
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
from .exceptions import ZoteroLocalError
import shutil
from .base_client import BaseZoteroClient
from .mixins.search import SearchMixin
from .mixins.files import FilesMixin
from .mixins.notes import NotesMixin

class ZoteroLocal(BaseZoteroClient, SearchMixin, FilesMixin, NotesMixin):
    """Zotero 本地 API 客户端。
    
    此类是与 Zotero 本地服务器交互的主要入口点，整合了文献管理、
    搜索、笔记和文件操作等功能。通过继承 BaseZoteroClient 和多个
    Mixin 类，提供了完整的 Zotero API 功能。
    
    Attributes:
        base_url: Zotero 本地服务器的基础 URL
        _session: HTTP 会话对象，用于复用连接
        _cache: 内部缓存字典
        
    Examples:
        基础用法：
        
        >>> from zoteroapi import ZoteroLocal
        >>> client = ZoteroLocal()
        >>> items = client.get_items_top(limit=10)
        >>> for item in items:
        ...     print(item['data']['title'])
        
        搜索文献：
        
        >>> results = client.search_items("machine learning")
        >>> print(f"找到 {len(results)} 篇文献")
        
        添加笔记：
        
        >>> note = client.add_item_note(
        ...     item_key="ABC123",
        ...     note_text="这是我的阅读笔记"
        ... )
    """
    
    def get_item(self, item_key: str) -> Dict:
        """获取单个文献条目。
        
        通过条目的唯一标识符获取其完整信息，包括元数据、标签、
        链接等所有相关数据。
        
        Args:
            item_key: 条目的唯一标识符（key）
            
        Returns:
            包含完整条目信息的字典，包含以下主要字段：
            - key: 条目唯一标识
            - version: 版本号
            - data: 核心数据（标题、作者、日期等）
            - meta: 元数据
            - links: 相关链接
            
        Raises:
            ZoteroLocalError: 当 API 请求失败时抛出
            ResourceNotFound: 当条目不存在时抛出
            
        Examples:
            >>> client = ZoteroLocal()
            >>> item = client.get_item("ABC123XYZ")
            >>> print(item['data']['title'])
            '深度学习研究'
        """
        response = self._make_request("GET", f"/items/{item_key}")
        return response.json()
        
    def get_items(self, limit: Optional[int] = None) -> List[Dict]:
        """获取所有文献条目。
        
        获取文献库中的所有条目，包括顶层条目和子条目（如笔记、附件等）。
        可以通过 limit 参数控制返回的数量。
        
        Args:
            limit: 限制返回的条目数量。如果为 None，则返回所有条目。
                  对于大型文献库，建议设置合理的 limit 值。
            
        Returns:
            条目列表，每个元素为包含完整条目信息的字典
            
        Raises:
            ZoteroLocalError: 当 API 请求失败时抛出
            
        Warning:
            获取所有条目可能需要较长时间，建议使用 limit 参数或
            使用 get_items_top() 只获取顶层条目。
            
        Examples:
            >>> client = ZoteroLocal()
            >>> # 获取前 50 个条目
            >>> items = client.get_items(limit=50)
            >>> print(f"获取了 {len(items)} 个条目")
        """
        params = {"limit": limit} if limit else None
        response = self._make_request("GET", "/items", params=params)
        return response.json()
        
    def get_collections(self) -> List[Dict]:
        """获取所有文献集。
        
        获取用户文献库中的所有文献集（Collections），包括顶层文献集
        和子文献集。
        
        Returns:
            文献集列表，每个元素包含文献集的信息：
            - key: 文献集唯一标识
            - data.name: 文献集名称
            - data.parentCollection: 父文献集 key（如果是子文献集）
            - data.numItems: 包含的条目数量
            
        Raises:
            ZoteroLocalError: 当 API 请求失败时抛出
            
        Examples:
            >>> client = ZoteroLocal()
            >>> collections = client.get_collections()
            >>> for coll in collections:
            ...     name = coll['data']['name']
            ...     num = coll['data'].get('numItems', 0)
            ...     print(f"{name}: {num} 篇")
        """
        response = self._make_request("GET", "/collections")
        return response.json()

    def get_item_file(self, item_key: str) -> BinaryIO:
        """
        获取条目的附件文件
        
        Args:
            item_key: 条目ID
            
        Returns:
            文件内容的二进制流
        """
        response = self._make_request("GET", f"/items/{item_key}/file")
        
        # 检查是否是压缩文件
        if (response.headers.get('Content-Type') == 'application/zip' and
            response.headers.get('Zotero-File-Compressed') == 'Yes'):
            z = zipfile.ZipFile(io.BytesIO(response.content))
            return io.BytesIO(z.read(z.namelist()[0]))
        
        return io.BytesIO(response.content)

    def download_file(self, item_key: str, path: Union[str, Path]) -> None:
        """
        下载条目的附件文件到指定路径

        Args:
            item_key: 条目ID（应该是附件项目的key）
            path: 保存路径
        """
        import shutil
        from urllib.parse import unquote

        try:
            # 获取附件项目信息
            item = self.get_item(item_key)

            # 检查是否是附件类型
            if item.get('data', {}).get('itemType') != 'attachment':
                raise ZoteroLocalError(f"Item {item_key} is not an attachment")

            # 从 enclosure 链接获取本地文件路径
            enclosure = item.get('links', {}).get('enclosure', {})
            file_url = enclosure.get('href', '')

            if not file_url:
                raise ZoteroLocalError(f"No file URL found for attachment {item_key}")

            # 处理 file:// URL
            if file_url.startswith('file://'):
                # 移除 file:// 前缀并解码 URL
                file_path = unquote(file_url[7:])
            else:
                file_path = unquote(file_url)

            # 检查源文件是否存在
            source_path = Path(file_path)
            if not source_path.exists():
                raise ZoteroLocalError(f"Source file not found: {file_path}")

            # 确保目标目录存在
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(source_path, path)

        except Exception as e:
            raise ZoteroLocalError(f"下载文件失败: {str(e)}")

    def upload_file(self, 
                   file_path: Union[str, Path], 
                   parent_item: Optional[str] = None,
                   title: Optional[str] = None) -> Dict:
        """
        上传文件作为附件
        
        Args:
            file_path: 文件路径
            parent_item: 父条目ID（可选）
            title: 附件标题（可选，默认使用文件名）
            
        Returns:
            上传结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ZoteroLocalError(f"文件不存在: {file_path}")
            
        # 准备上传数据
        file_data = {
            "filename": file_path.name,
            "title": title or file_path.name,
            "contentType": self._guess_mimetype(file_path),
            "md5": self._calculate_md5(file_path)
        }
        
        if parent_item:
            file_data["parentItem"] = parent_item
            
        # 创建附件条目
        response = self._make_request(
            "POST", 
            "/items", 
            data={"items": [file_data]}
        )
        
        item_key = response.json()["successful"][0]["key"]
        
        # 上传文件内容
        with open(file_path, 'rb') as f:
            self._make_request(
                "POST",
                f"/items/{item_key}/file",
                files={"file": f}
            )
            
        return self.get_item(item_key)

    def _guess_mimetype(self, file_path: Path) -> str:
        """猜测文件的MIME类型"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'
        
    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件的MD5值"""
        import hashlib
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def get_items_top(self, limit: int = 10) -> List[Dict]:
        """
        获取顶层条目

        Args:
            limit: 限制返回的条目数量

        Returns:
            顶层条目列表
        """
        params = {"limit": limit}
        response = self._make_request("GET", "/items/top", params=params)
        return response.json()

    def get_collection(self, collection_key: str) -> Dict:
        """
        获取单个文献集

        Args:
            collection_key: 文献集的唯一标识符

        Returns:
            文献集信息
        """
        response = self._make_request("GET", f"/collections/{collection_key}")
        return response.json()

    def get_collection_items(self, collection_key: str) -> List[Dict]:
        """
        获取文献集中的所有条目

        Args:
            collection_key: 文献集的唯一标识符

        Returns:
            条目列表
        """
        response = self._make_request("GET", f"/collections/{collection_key}/items")
        return response.json()

    def get_tags(self) -> List[str]:
        """
        获取所有标签

        Returns:
            标签列表
        """
        response = self._make_request("GET", "/tags")
        return response.json()

    def get_item_by_key(self, item_key: str) -> Dict:
        """
        通过key获取单个条目

        Args:
            item_key: 条目的唯一标识符

        Returns:
            条目信息
        """
        response = self._make_request("GET", f"/items/{item_key}")
        return response.json()

    def get_item_attachment_href(self, item_key: str) -> str:
        """
        获取条目附件的直接下载链接
        
        Args:
            item_key: 条目ID
            
        Returns:
            附件的直接下载链接
            
        Raises:
            ZoteroLocalError: 当无法获取附件链接或附件不是PDF时抛出
        """
        # 获取条目信息
        item_result = self.get_item_by_key(item_key)
        
        # 检查附件信息
        links = item_result.get('links', {})
        attachment = links.get('attachment')
        
        if not attachment:
            raise ZoteroLocalError(f"条目 {item_key} 没有附件")
            
        if attachment.get('attachmentType') != 'application/pdf':
            raise ZoteroLocalError(f"条目 {item_key} 的附件不是PDF格式")
        
        # 获取附件href
        href = attachment.get('href')
        if not href:
            raise ZoteroLocalError(f"无法获取条目 {item_key} 的附件链接")
            
        # 获取附件详细信息
        try:
            response = requests.get(href)
            response.raise_for_status()
            attachment_data = response.json()
        except requests.RequestException as e:
            raise ZoteroLocalError(f"获取附件信息失败: {str(e)}")
            
        # 提取下载链接
        try:
            attachment_links = attachment_data.get('links', {})
            attachment_href = attachment_links.get('enclosure', {}).get('href')
            
            if not attachment_href:
                raise ZoteroLocalError(f"无法获取条目 {item_key} 的附件下载链接")
                
            return attachment_href
            
        except (KeyError, TypeError) as e:
            raise ZoteroLocalError(f"解析附件信息失败: {str(e)}")
        
    def get_pmid(self, item_key: str) -> str:
        """Get PMID for a given item.

        Searches for PMID in multiple possible locations:
        1. Direct 'PMID' field in data (most common from PubMed import)
        2. 'extra' field with 'PMID:' prefix
        3. 'url' field (pubmed.ncbi.nlm.nih.gov/PMID)
        4. 'archive' field
        5. 'notes' field

        Args:
            item_key: The Zotero item key

        Returns:
            str: The PMID if found, empty string if not found

        Raises:
            ZoteroLocalError: If the API request fails
        """
        try:
            item = self.get_item(item_key)
            if not item:
                return ""

            data = item.get('data', {})

            # Method 1: Check direct PMID field (most common from PubMed import)
            pmid_direct = data.get('PMID', '')
            if pmid_direct:
                return str(pmid_direct)

            # Method 2: Try to find PMID in extra field
            extra = data.get('extra', '')
            if extra:
                for line in extra.split('\n'):
                    if line.startswith('PMID:'):
                        return line.split(':')[1].strip()

            # Method 3: Try to find PMID in URL field
            # Often in format: https://pubmed.ncbi.nlm.nih.gov/36434096/
            url = data.get('url', '')
            if url:
                import re
                # Match PMID in various URL formats
                match = re.search(r'pubmed\.ncbi\.nlm\..nih\.gov/(\d+)', url)
                if match:
                    return match.group(1)

            # Method 4: Try archive field
            archive = data.get('archive', '')
            if archive:
                import re
                match = re.search(r'(\d{8})', archive)
                if match:
                    return match.group(1)

            # Method 5: Try notes field
            notes = data.get('notes', [])
            if notes:
                for note in notes:
                    if isinstance(note, dict):
                        note_content = note.get('note', '')
                    else:
                        note_content = str(note)
                    import re
                    match = re.search(r'PMID[:\s]+(\d+)', note_content, re.IGNORECASE)
                    if match:
                        return match.group(1)

            return ""

        except Exception as e:
            raise ZoteroLocalError(f"Failed to get PMID: {str(e)}")

    def copy_attachment_to_downloads(self, file_uri: str, download_dir: str = None) -> str:
        """
        Copy a Zotero attachment file to downloads directory
        
        Args:
            file_uri: File URI (e.g., file:///path/to/file.pdf)
            download_dir: Target download directory (default: user's Downloads folder)
            
        Returns:
            Path to the copied file
            
        Raises:
            ZoteroLocalError: If file copying fails
        """
        try:
            # Normalize the file path
            file_path = self._normalize_path(file_uri)
            
            # Get file name from path
            file_name = os.path.basename(file_path)
            
            # Use system Downloads folder if no download_dir specified
            if not download_dir:
                download_dir = str(Path.home() / "Downloads")
                
            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Construct destination path
            dest_path = os.path.join(download_dir, file_name)
            
            # Copy the file
            shutil.copy2(file_path, dest_path)
            
            return dest_path
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to copy file: {str(e)}")