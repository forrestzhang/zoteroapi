import requests
import json
import os
import zipfile
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO, Any
from .exceptions import ZoteroLocalError, APIError, ResourceNotFound
import os
import shutil
from urllib.parse import unquote
from pathlib import Path

class ZoteroLocal:
    """Zotero本地API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:23119/api/users/000000/"):
        """初始化Zotero本地API客户端"""
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._cache = {}
        
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     headers: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> requests.Response:
        """发送HTTP请求到Zotero API"""
        url = f"{self.base_url}{endpoint}"
        
        params = params or {}
        if 'format' not in params:
            params['format'] = 'json'
            
        headers = headers or {}
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ZoteroLocalError(f"API请求失败: {str(e)}")

    def get_item(self, item_key: str) -> Dict:
        """获取单个条目"""
        response = self._make_request("GET", f"/items/{item_key}")
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
            item_key: 条目ID
            path: 保存路径
        """
        try:
            # 直接从API获取文件内容
            response = self._request(
                method="GET",
                path=f"items/{item_key}/file",
                params={"format": "raw"},  # 使用raw格式获取文件内容
                raw_response=True  # 获取原始响应而不是JSON
            )
            
            # 确保目标目录存在
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(path, 'wb') as f:
                f.write(response.content)
                
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

    def get_items(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取所有条目

        Args:
            limit: 限制返回的条目数量

        Returns:
            条目列表
        """
        params = {"limit": limit} if limit else None
        response = self._make_request("GET", "/items", params=params)
        return response.json()

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

    def get_collections(self) -> List[Dict]:
        """
        获取所有文献集

        Returns:
            文献集列表
        """
        response = self._make_request("GET", "/collections")
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

    def search_items(self, query: str) -> List[Dict]:
        """
        搜索条目

        Args:
            query: 搜索关键词

        Returns:
            匹配的条目列表
        """
        params = {"q": query}
        response = self._make_request("GET", "/items", params=params)
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

    def _request(
        self, 
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        raw_response: bool = False,
        **kwargs
    ) -> Any:
        """Make HTTP request with error handling"""
        url = self._build_url(path)
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                **kwargs
            )
            response.raise_for_status()
            
            # Return raw response if requested
            if raw_response:
                return response
            
            return response.json() if response.content else None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ResourceNotFound(f"Resource not found: {url}")
            raise APIError(f"Request failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        
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
            # Remove 'file:///' prefix and decode URL encoding
            file_path = unquote(file_uri.replace('file:///', ''))
            
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

    def get_pmid(self, item_key: str) -> str:
        """Get PMID for a given item.
        
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
            
            # Try to find PMID in extra field
            extra = item.get('data', {}).get('extra', '')
            if extra:
                for line in extra.split('\n'):
                    if line.startswith('PMID:'):
                        return line.split(':')[1].strip()
                    
            return ""
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to get PMID: {str(e)}")